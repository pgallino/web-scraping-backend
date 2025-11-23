import pytest

from src.adapters.db.repositories import tool_repository as repo_module
from src.domain.tool import Tool


class FakeModel:
    def __init__(self, id=None, name=None, description=None, link=None):
        self.id = id
        self.name = name
        self.description = description
        self.link = link

# Provide class-level attributes so expressions like ToolModel.id don't raise
# AttributeError when code references column attributes on the model class.
FakeModel.id = None
FakeModel.name = None
FakeModel.description = None
FakeModel.link = None


class FakeResult:
    def __init__(self, scalar=None, scalars_list=None):
        self._scalar = scalar
        self._scalars_list = scalars_list or []

    def scalar_one_or_none(self):
        return self._scalar

    def scalars(self):
        class _S:
            def __init__(self, lst):
                self._lst = lst

            def all(self):
                return self._lst

        return _S(self._scalars_list)


class FakeSession:
    _id_counter = 1

    def __init__(self, store=None, scalar_result=None, scalars_list=None):
        # store: dict[id]->FakeModel
        self.store = store or {}
        self._scalar = scalar_result
        self._scalars = scalars_list
        self._added = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, query):
        # ignore query object; return configured fake results
        if self._scalar is not None:
            return FakeResult(scalar=self._scalar)
        if self._scalars is not None:
            return FakeResult(scalars_list=self._scalars)
        # default: if store has multiple, return scalars list
        return FakeResult(scalars_list=list(self.store.values()))

    def add(self, model):
        self._added = model

    async def commit(self):
        # emulate DB assigned id on insert
        if self._added is not None and getattr(self._added, "id", None) in (None, 0):
            self._added.id = FakeSession._id_counter
            FakeSession._id_counter += 1

    async def refresh(self, model):
        # noop; id already set by commit
        return None

    async def delete(self, model):
        if getattr(model, "id", None) in self.store:
            del self.store[model.id]


class DummySelectable:
    """Minimal object that mimics SQLAlchemy selectable with a `where` method
    so repository code can call `select(...).where(...)` without error.
    """
    def where(self, *args, **kwargs):
        return self


@pytest.mark.asyncio
async def test_get_by_id_found(monkeypatch):
    fake = FakeModel(id=1, name="t1", description="d", link="l")
    # patch the imported ToolModel and AsyncSessionLocal
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    # SQLAlchemy's select(...) is used only to build a query; replace it with a stub
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: FakeSession(scalar_result=fake))

    repo = repo_module.SqlAlchemyToolRepository()
    res = await repo.get_by_id(1)
    assert isinstance(res, Tool)
    assert res.id == 1
    assert res.name == "t1"


@pytest.mark.asyncio
async def test_get_by_id_not_found(monkeypatch):
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: FakeSession(scalar_result=None))

    repo = repo_module.SqlAlchemyToolRepository()
    res = await repo.get_by_id(42)
    assert res is None


@pytest.mark.asyncio
async def test_get_by_name_found(monkeypatch):
    fake = FakeModel(id=2, name="tool-x", description="d2", link="l2")
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: FakeSession(scalar_result=fake))

    repo = repo_module.SqlAlchemyToolRepository()
    res = await repo.get_by_name("tool-x")
    assert isinstance(res, Tool)
    assert res.name == "tool-x"


@pytest.mark.asyncio
async def test_create(monkeypatch):
    # Fake session will assign id on commit
    fake_session = FakeSession()
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session)

    repo = repo_module.SqlAlchemyToolRepository()
    tool_in = Tool(id=0, name="new", description="d", link="l")
    res = await repo.create(tool_in)
    assert isinstance(res, Tool)
    assert res.id == 1
    assert res.name == "new"


@pytest.mark.asyncio
async def test_list_all(monkeypatch):
    s1 = FakeModel(id=1, name="a", description="d", link="l")
    s2 = FakeModel(id=2, name="b", description="d2", link="l2")
    fake_session = FakeSession(store={1: s1, 2: s2})
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session)

    repo = repo_module.SqlAlchemyToolRepository()
    res = await repo.list_all()
    assert isinstance(res, list)
    assert len(res) == 2


@pytest.mark.asyncio
async def test_update_found(monkeypatch):
    model = FakeModel(id=3, name="old", description="od", link="ol")
    store = {3: model}
    fake_session = FakeSession(store=store, scalar_result=model)
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session)

    repo = repo_module.SqlAlchemyToolRepository()
    updated_tool = Tool(id=3, name="new", description="nd", link="nl")
    res = await repo.update(updated_tool)
    assert isinstance(res, Tool)
    assert res.name == "new"


@pytest.mark.asyncio
async def test_update_not_found(monkeypatch):
    fake_session = FakeSession(scalar_result=None)
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session)

    repo = repo_module.SqlAlchemyToolRepository()
    updated_tool = Tool(id=999, name="x", description="d", link="l")
    res = await repo.update(updated_tool)
    assert res is None


@pytest.mark.asyncio
async def test_delete_found_and_not_found(monkeypatch):
    model = FakeModel(id=4, name="t4", description="d", link="l")
    store = {4: model}
    fake_session = FakeSession(store=store, scalar_result=model)
    monkeypatch.setattr(repo_module, "ToolModel", FakeModel)
    monkeypatch.setattr(repo_module, "select", lambda *a, **k: DummySelectable())
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session)

    repo = repo_module.SqlAlchemyToolRepository()
    ok = await repo.delete(4)
    assert ok is True

    # not found
    fake_session2 = FakeSession(scalar_result=None)
    monkeypatch.setattr(repo_module, "AsyncSessionLocal", lambda: fake_session2)
    ok2 = await repo.delete(999)
    assert ok2 is False
