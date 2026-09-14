import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.registry import ToolRegistry
from app.agent.tools.artifact_generator import ArtifactGeneratorTool
from app.services.ingestion_service import IngestionService
from app.services.artifact_service import ArtifactService
from app.services.session_service import SessionService
from app.services.chat_service import ChatService
from app.schemas.artifact import ArtifactCreate
from app.schemas.session import SessionCreate
from app.schemas.chat import ChatRequest
from app.agent.providers import MockAgentProvider
from app.errors import EntityNotFoundError
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_artifact_tool_registration(test_db: AsyncSession):
    """Verify generate_artifact is registered in ToolRegistry with valid parameters."""
    registry = ToolRegistry(test_db)
    tool = registry.get_tool("generate_artifact")
    assert tool is not None
    assert isinstance(tool, ArtifactGeneratorTool)
    assert tool.name == "generate_artifact"

    schema = tool.to_schema()
    assert schema["type"] == "function"
    fn = schema["function"]
    assert fn["name"] == "generate_artifact"
    params = fn["parameters"]["properties"]
    assert "artifact_type" in params
    assert "title" in params
    assert "topic" in params
    assert "instructions" in params
    assert "source_url_or_guest" in params


@pytest.mark.asyncio
async def test_markdown_artifact_generation(test_db: AsyncSession):
    """Verify Markdown artifact generation produces valid headings, structure, and word count."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    tool = ArtifactGeneratorTool(test_db)
    result = await tool.execute(
        artifact_type="markdown",
        title="PRD: Self-Serve Product Onboarding",
        topic="Elena Verna product-led growth onboarding activation",
        instructions="Focus on activation metrics and drop-off risks",
    )

    assert result["status"] == "complete"
    assert result["type"] == "markdown"
    assert result["title"] == "PRD: Self-Serve Product Onboarding"
    assert result["word_count"] > 250
    assert result["allow_scripts"] is False

    content = result["content"]
    assert content.startswith("# PRD: Self-Serve Product Onboarding")
    assert "## Executive Summary" in content
    assert "## 1. Problem Statement & Strategic Context" in content
    assert "## 2. Empirical Grounding & Transcript Evidence" in content
    assert "## 3. Operational Implementation Protocol" in content
    assert "## Tactical Requirements" in content
    assert len(result["citations"]) > 0


@pytest.mark.asyncio
async def test_html_artifact_generation(test_db: AsyncSession):
    """Verify complete standalone HTML/CSS generation with embedded styles and no external scripts."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    tool = ArtifactGeneratorTool(test_db)
    result = await tool.execute(
        artifact_type="html",
        title="Growth Loop Architecture",
        topic="Casey Winters compounding growth loops and retention",
    )

    assert result["status"] == "complete"
    assert result["type"] == "html"
    assert result["title"] == "Growth Loop Architecture"
    assert result["word_count"] > 100
    assert result["allow_scripts"] is False

    html_content = result["content"]
    assert "<!DOCTYPE html>" in html_content
    assert "<html lang=\"en\">" in html_content
    assert "<head>" in html_content
    assert "<style>" in html_content
    assert "<body>" in html_content
    assert "Content-Security-Policy" in html_content
    assert "<script" not in html_content.lower()


@pytest.mark.asyncio
async def test_html_security_constraints(test_db: AsyncSession):
    """Verify sanitizer strips dangerous scripts, event handlers, and javascript: URIs."""
    tool = ArtifactGeneratorTool(test_db)

    malicious_payload = (
        '<!DOCTYPE html><html><head><script>alert("hack")</script></head>'
        '<body onload="stealData()">'
        '<a href="javascript:doEvil()">Click</a>'
        '<base target="_top">'
        '<button onclick="hack()">Test</button>'
        '</body></html>'
    )
    clean = tool._sanitize_html(malicious_payload)

    assert "<script>" not in clean
    assert "alert(" not in clean
    assert "onload=" not in clean
    assert 'href="javascript:' not in clean
    assert 'target="_top"' not in clean
    assert "onclick=" not in clean


@pytest.mark.asyncio
async def test_artifact_persistence_and_retrieval(test_db: AsyncSession):
    """Verify database persistence and retrieval via ArtifactService."""
    session = await SessionService.create_session(test_db, SessionCreate(title="Artifact Test Session"))

    # Create markdown artifact
    art = await ArtifactService.create_artifact(
        db=test_db,
        data=ArtifactCreate(
            sessionId=session.id,
            title="Growth Framework Spec",
            type="markdown",
            content="# Spec Content\n\n- Point 1\n- Point 2",
            wordCount=12,
            sourceCount=1,
            allowScripts=False,
        ),
    )
    assert art.id.startswith("artifact-")
    assert art.title == "Growth Framework Spec"
    assert art.type == "markdown"
    assert art.word_count == 12

    # Retrieve artifact
    retrieved = await ArtifactService.get_artifact(test_db, art.id)
    assert retrieved.id == art.id
    assert retrieved.content == art.content
    assert retrieved.session_id == session.id

    # List artifacts
    all_arts = await ArtifactService.list_artifacts(test_db, session_id=session.id)
    assert len(all_arts) >= 1
    assert any(a.id == art.id for a in all_arts)


@pytest.mark.asyncio
async def test_malformed_empty_artifact_handling(test_db: AsyncSession):
    """Verify rejection of empty titles and missing sessions."""
    # Empty title should fail Pydantic validation
    with pytest.raises(Exception):
        ArtifactCreate(
            sessionId="valid-session",
            title="",
            type="markdown",
            content="Some text",
        )

    # Missing session should raise EntityNotFoundError in service
    with pytest.raises(EntityNotFoundError):
        await ArtifactService.create_artifact(
            db=test_db,
            data=ArtifactCreate(
                sessionId="non-existent-session-id",
                title="Orphan Artifact",
                type="markdown",
                content="Some text",
            ),
        )


@pytest.mark.asyncio
async def test_grounded_artifact_citation_propagation(test_db: AsyncSession):
    """Verify verified transcript citations are propagated without fabrication."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    tool = ArtifactGeneratorTool(test_db)
    result = await tool.execute(
        artifact_type="markdown",
        title="Retention Mechanics",
        topic="Casey Winters retention loops",
    )

    assert result["status"] == "complete"
    assert len(result["citations"]) > 0
    for citation in result["citations"]:
        assert citation["guest"] is not None
        assert citation["episode_title"] is not None
        assert "quote" in citation
        assert len(citation["quote"]) > 0


@pytest.mark.asyncio
async def test_unsupported_grounded_artifact_request(test_db: AsyncSession):
    """Verify out-of-domain requests return low-evidence and 0 citations."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    tool = ArtifactGeneratorTool(test_db)
    result = await tool.execute(
        artifact_type="markdown",
        title="Solana Staking Economy",
        topic="Solana staking rewards crypto tokenomics and validator yield",
    )

    assert result["status"] == "low-evidence"
    assert "Insufficient transcript evidence" in result["content"]
    assert len(result["citations"]) == 0
    assert result["word_count"] == 0


@pytest.mark.asyncio
async def test_chat_service_markdown_artifact_integration(test_db: AsyncSession):
    """Verify ChatService routes PRD request, generates artifact, persists it, and returns it."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)
    session = await SessionService.create_session(test_db, SessionCreate(title="Chat Artifact Session"))

    mock_provider = MockAgentProvider()
    response = await ChatService.process_chat(
        db=test_db,
        request=ChatRequest(
            session_id=session.id,
            content="Create a Markdown PRD for Casey Winters retention curve framework",
        ),
        custom_provider=mock_provider,
    )

    assert response.artifact is not None
    assert response.artifact.type == "markdown"
    assert "Artifact:" in response.artifact.title
    assert response.artifact.word_count > 100
    assert response.assistant_message.artifact_id == response.artifact.id

    # Verify persisted in database
    db_art = await ArtifactService.get_artifact(test_db, response.artifact.id)
    assert db_art is not None
    assert db_art.title == response.artifact.title


@pytest.mark.asyncio
async def test_chat_service_html_artifact_integration(test_db: AsyncSession):
    """Verify ChatService routes HTML landing page request, persists HTML artifact, and returns it."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)
    session = await SessionService.create_session(test_db, SessionCreate(title="HTML Artifact Session"))

    mock_provider = MockAgentProvider()
    response = await ChatService.process_chat(
        db=test_db,
        request=ChatRequest(
            session_id=session.id,
            content="Turn this into an HTML landing page for Elena Verna PLG loops",
        ),
        custom_provider=mock_provider,
    )

    assert response.artifact is not None
    assert response.artifact.type == "html"
    assert "<!DOCTYPE html>" in response.artifact.content
    assert response.artifact.allow_scripts is False
    assert response.assistant_message.artifact_id == response.artifact.id
