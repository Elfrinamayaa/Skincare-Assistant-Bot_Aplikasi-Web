def post_chat(client, message, theme="skincare"):
    return client.post("/api/chat", json={"theme": theme, "message": message})


def test_halaman_utama_dan_chat(client):
    assert client.get("/").status_code == 200
    page = client.get("/chat/skincare")
    assert page.status_code == 200 and b"SkinTant" in page.data


def test_tema_tidak_ada_404(client):
    assert client.get("/chat/tidak-ada").status_code == 404
    res = client.get("/api/history/tidak-ada")
    assert res.status_code == 404 and "error" in res.get_json()


def test_api_themes(client):
    ids = [t["id"] for t in client.get("/api/themes").get_json()]
    assert "skincare" in ids


def test_api_chat_sukses(client):
    data = post_chat(client, "Skincare untuk kulit berminyak apa?").get_json()
    assert data["intent"] == "oily_skin" and "facial wash" in data["reply"]


def test_api_chat_validasi(client):
    assert post_chat(client, "   ").status_code == 400
    assert post_chat(client, "halo", theme="xyz").status_code == 400
    assert post_chat(client, "a" * 501).status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    post_chat(client, "halo")
    rows = client.get("/api/history/skincare").get_json()
    assert [r["role"] for r in rows] == ["user", "bot"]
    client.delete("/api/history/skincare")
    assert client.get("/api/history/skincare").get_json() == []


def test_riwayat_antar_sesi_terpisah(tmp_path):
    from app import create_app
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "a.db")})
    a, b = app.test_client(), app.test_client()
    post_chat(a, "halo")
    assert b.get("/api/history/skincare").get_json() == []


def test_statistik_dan_pertanyaan_tak_dikenali(client):
    post_chat(client, "halo")
    post_chat(client, "resep nasi goreng")
    stats = client.get("/api/stats/skincare").get_json()
    assert stats["total_questions"] == 2 and stats["fallback"] == 1
    admin = client.get("/admin/skincare")
    assert admin.status_code == 200 and b"resep nasi goreng" in admin.data


def test_admin_dilindungi_kunci(tmp_path):
    from app import create_app
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "k.db"), "ADMIN_KEY": "rahasia"})
    c = app.test_client()
    assert c.get("/admin/skincare").status_code == 403
    assert c.get("/admin/skincare?key=rahasia").status_code == 200


def test_explain(client):
    data = client.post("/api/explain", json={"theme": "skincare", "message": "jerawat"}).get_json()
    assert data["candidates"][0]["intent"] == "acne_skin"
