from scripts.make_space import make_space


def test_space_folder_holds_what_the_docker_build_needs(tmp_path):
    out = make_space(tmp_path / "space")
    for rel in ("Dockerfile", "README.md", "requirements.txt", "scripts/fetch_model.py", "api/main.py",
                "src/bahaana/engine.py", "shared/holidays_2026.json"):
        assert (out / rel).is_file(), rel
    assert "sdk: docker" in (out / "README.md").read_text(encoding="utf-8")
    assert "app_port: 7860" in (out / "README.md").read_text(encoding="utf-8")


def test_space_folder_leaves_out_caches_and_web(tmp_path):
    out = make_space(tmp_path / "space")
    names = {p.name for p in out.rglob("*")}
    assert "__pycache__" not in names and "web" not in names and "models" not in names


def test_rebuilding_keeps_the_spaces_git_folder(tmp_path):
    out = tmp_path / "space"
    (out / ".git").mkdir(parents=True)
    (out / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    (out / "stale.txt").write_text("old")
    make_space(out)
    assert (out / ".git" / "HEAD").is_file()
    assert not (out / "stale.txt").exists()
