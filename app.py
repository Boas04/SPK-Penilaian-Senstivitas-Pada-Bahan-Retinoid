import json
import os
from typing import List, Dict, Tuple
import math
import jinja2
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash


# =========================
# In-memory Templates (single-file app)
# =========================
TEMPLATES: Dict[str, str] = {
    "base.html": """<!doctype html>
<html lang=\"id\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>SPK | TOPSIS & Profile Matching</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <script src=\"https://cdn.plot.ly/plotly-2.27.0.min.js\"></script>
    <style>
      body { background-color: #f8f9fa; }
      .navbar-brand { font-weight: 700; letter-spacing: 0.5px; }
      .table thead th { white-space: nowrap; }
      .card-header h5, .card-header h4 { margin: 0; }
    </style>
</head>
<body>
<nav class=\"navbar navbar-expand-lg navbar-dark bg-dark\">
  <div class=\"container-fluid\">
    <a class=\"navbar-brand\" href=\"/\">SPK</a>
    <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#navbarNav\">
      <span class=\"navbar-toggler-icon\"></span>
    </button>
    <div class=\"collapse navbar-collapse\" id=\"navbarNav\">
      <ul class=\"navbar-nav\">
        <li class=\"nav-item\"><a class=\"nav-link\" href=\"/\">Data</a></li>
        <li class=\"nav-item\"><a class=\"nav-link\" href=\"/profile-matching\">Profile Matching</a></li>
        <li class=\"nav-item\"><a class=\"nav-link\" href=\"/topsis\">TOPSIS</a></li>
        <li class=\"nav-item\"><a class=\"nav-link\" href=\"/comparison\">Perbandingan</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class=\"container my-4\">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class=\"alert alert-{{ category }} alert-dismissible fade show\" role=\"alert\">
            {{ message }}
            <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
</div>

<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js\"></script>
</body>
</html>""",

    "index.html": """{% extends 'base.html' %}
{% block content %}
<div class=\"row mb-4\">
    <div class=\"col-md-12\">
        <div class=\"card\">
            <div class=\"card-header d-flex justify-content-between align-items-center\">
                <h4 class=\"mb-0\">Data Kriteria</h4>
                <div>
                     <button type=\"button\" class=\"btn btn-sm btn-outline-success\" data-bs-toggle=\"modal\" data-bs-target=\"#addCriteriaModal\">
                        + Tambah Kriteria
                    </button>
                    <button type=\"button\" class=\"btn btn-sm btn-outline-danger\" data-bs-toggle=\"modal\" data-bs-target=\"#resetModal\">
                        Reset Default
                    </button>
                </div>
            </div>
            <div class=\"card-body\">
                <div class=\"table-responsive\">
                    <table class=\"table table-hover table-bordered align-middle\">
                        <thead class=\"table-light\">
                            <tr>
                                <th>Kode</th>
                                <th>Nama Kriteria</th>
                                <th>Atribut</th>
                                <th style=\"width: 50px;\">Aksi</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in criteria %}
                            <tr>
                                <td>{{ c.code }}</td>
                                <td>{{ c.name }}</td>
                                <td>
                                    {% if c.attr == 'benefit' %}
                                    <span class=\"badge bg-success\">Benefit</span>
                                    {% else %}
                                    <span class=\"badge bg-danger\">Cost</span>
                                    {% endif %}
                                </td>
                                <td class=\"text-center\">
                                    <a href=\"/delete_criteria/{{ loop.index0 }}\" class=\"btn btn-sm btn-danger\" onclick=\"return confirm('Hapus kriteria ini? Data nilai alternatif untuk kriteria ini akan hilang.')\">×</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<div class=\"row\">
    <div class=\"col-md-12\">
        <div class=\"card\">
            <div class=\"card-header\">
                <h4 class=\"mb-0\">Data Alternatif</h4>
            </div>
            <div class=\"card-body\">
                <p class=\"text-muted\">Silakan edit nilai alternatif di bawah ini.</p>
                
                <form action=\"/\" method=\"POST\">
                    <div class=\"table-responsive\">
                        <table class=\"table table-hover table-bordered align-middle\">
                            <thead class=\"table-light\">
                                <tr>
                                    <th>Alternatif</th>
                                    {% for c in criteria %}
                                    <th>{{ c.code }} <br><span class=\"small fw-normal text-muted\">{{ c.name }}</span></th>
                                    {% endfor %}
                                    <th style=\"width: 50px;\">Aksi</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in data %}
                                <tr>
                                    <td>
                                        <input type=\"text\" class=\"form-control\" name=\"Alternatif_{{ loop.index0 }}\" value=\"{{ row['Alternatif'] }}\" required>
                                    </td>
                                    {% for c in criteria %}
                                    <td>
                                        <input type=\"number\" step=\"0.01\" class=\"form-control\" name=\"{{ c.code }}_{{ loop.index0 }}\" value=\"{{ row[c.code] }}\" required>
                                    </td>
                                    {% endfor %}
                                    <td class=\"text-center\">
                                        <a href=\"/delete/{{ loop.index0 }}\" class=\"btn btn-sm btn-danger\" onclick=\"return confirm('Hapus baris ini?')\">×</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class=\"d-flex justify-content-between mt-3\">
                        <a href=\"/add\" class=\"btn btn-outline-secondary\">+ Tambah Alternatif</a>
                        <button type=\"submit\" class=\"btn btn-primary\">Simpan Perubahan</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Add Criteria Modal -->
<div class=\"modal fade\" id=\"addCriteriaModal\" tabindex=\"-1\">
  <div class=\"modal-dialog\">
    <div class=\"modal-content\">
      <form action=\"/add_criteria\" method=\"POST\">
          <div class=\"modal-header\">
            <h5 class=\"modal-title\">Tambah Kriteria</h5>
            <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\"></button>
          </div>
          <div class=\"modal-body\">
            <div class=\"mb-3\">
                <label class=\"form-label\">Kode (Contoh: K6)</label>
                <input type=\"text\" class=\"form-control\" name=\"code\" required>
            </div>
            <div class=\"mb-3\">
                <label class=\"form-label\">Nama Kriteria</label>
                <input type=\"text\" class=\"form-control\" name=\"name\" required>
            </div>
            <div class=\"mb-3\">
                <label class=\"form-label\">Atribut</label>
                <select class=\"form-select\" name=\"attr\">
                    <option value=\"benefit\">Benefit</option>
                    <option value=\"cost\">Cost</option>
                </select>
            </div>
          </div>
          <div class=\"modal-footer\">
            <button type=\"button\" class=\"btn btn-secondary\" data-bs-dismiss=\"modal\">Batal</button>
            <button type=\"submit\" class=\"btn btn-success\">Tambah</button>
          </div>
      </form>
    </div>
  </div>
</div>

<!-- Reset Modal -->
<div class=\"modal fade\" id=\"resetModal\" tabindex=\"-1\">
  <div class=\"modal-dialog\">
    <div class=\"modal-content\">
      <div class=\"modal-header\">
        <h5 class=\"modal-title\">Reset Data</h5>
        <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\"></button>
      </div>
      <div class=\"modal-body\">
        Apakah Anda yakin ingin mereset data Kriteria dan Alternatif ke default awal?
      </div>
      <div class=\"modal-footer\">
        <button type=\"button\" class=\"btn btn-secondary\" data-bs-dismiss=\"modal\">Batal</button>
        <a href=\"/reset\" class=\"btn btn-danger\">Reset</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

    "topsis.html": """{% extends 'base.html' %}
{% block content %}
<div class=\"row\">
    <div class=\"col-md-4\">
        <div class=\"card\">
            <div class=\"card-header\">
                <h5 class=\"mb-0\">Konfigurasi TOPSIS</h5>
            </div>
            <div class=\"card-body\">
                <form action=\"/topsis\" method=\"POST\">
                    <h6 class=\"text-muted mb-3\">Bobot & Atribut Kriteria</h6>
                    {% for c in criteria %}
                    <div class=\"mb-3 border-bottom pb-2\">
                        <label class=\"form-label fw-bold\">{{ c.code }} <span class=\"fw-normal text-muted\">- {{ c.name }}</span></label>
                        <div class=\"row g-2\">
                            <div class=\"col-6\">
                                <label class=\"small text-muted\">Bobot</label>
                                <input type=\"number\" step=\"0.01\" class=\"form-control form-control-sm\" name=\"weight_{{ c.code }}\" value=\"{{ defaults.get('weight_' + c.code, 1) }}\" required>
                            </div>
                            <div class=\"col-6\">
                                <label class=\"small text-muted\">Atribut</label>
                                <select class=\"form-select form-select-sm\" name=\"attr_{{ c.code }}\">
                                    <option value=\"benefit\" {{ 'selected' if defaults.get('attr_' + c.code, c.attr) == 'benefit' else '' }}>Benefit</option>
                                    <option value=\"cost\" {{ 'selected' if defaults.get('attr_' + c.code, c.attr) == 'cost' else '' }}>Cost</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    {% endfor %}

                    <button type=\"submit\" class=\"btn btn-primary w-100\">Hitung TOPSIS</button>
                </form>
            </div>
        </div>
    </div>

    <div class=\"col-md-8\">
        {% if results is not none %}
        <div class=\"card mb-4\">
            <div class=\"card-header bg-primary text-white\">
                <h5 class=\"mb-0\">Hasil Perankingan TOPSIS</h5>
            </div>
            <div class=\"card-body\">
                <div class=\"table-responsive\">
                    <table class=\"table table-striped table-hover\">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Alternatif</th>
                                <th>D+ (Jarak Ideal Pos)</th>
                                <th>D- (Jarak Ideal Neg)</th>
                                <th>Nilai Preferensi (V)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in results %}
                            <tr class=\"{{ 'table-primary fw-bold' if loop.first else '' }}\">
                                <td>{{ row['Rank_TOPSIS']|int }}</td>
                                <td>{{ row['Alternatif'] }}</td>
                                <td>{{ "%.4f"|format(row['D_Plus']) }}</td>
                                <td>{{ "%.4f"|format(row['D_Minus']) }}</td>
                                <td>{{ "%.4f"|format(row['V_TOPSIS']) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class=\"card\">
            <div class=\"card-header\">
                <h5 class=\"mb-0\">Visualisasi Skor Preferensi</h5>
            </div>
            <div class=\"card-body\">
                <div id=\"chart\"></div>
            </div>
        </div>

        <script>
            var chartData = {{ chart_json | safe }};
            Plotly.newPlot('chart', chartData.data, chartData.layout);
        </script>
        {% else %}
        <div class=\"alert alert-info\">
            <h4 class=\"alert-heading\">Belum ada hasil!</h4>
            <p>Silakan atur konfigurasi di sebelah kiri dan klik tombol \"Hitung TOPSIS\" untuk melihat hasil.</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    "pm.html": """{% extends 'base.html' %}
{% block content %}
<div class=\"row\">
    <div class=\"col-md-4\">
        <div class=\"card\">
            <div class=\"card-header\">
                <h5 class=\"mb-0\">Konfigurasi Profile Matching</h5>
            </div>
            <div class=\"card-body\">
                <form action=\"/profile-matching\" method=\"POST\">
                    <h6 class=\"text-muted mb-3\">Target & Bobot per Kriteria</h6>
                    {% for c in criteria %}
                    <div class=\"mb-3 border-bottom pb-2\">
                        <label class=\"form-label fw-bold\">{{ c.code }} <span class=\"fw-normal text-muted\">- {{ c.name }}</span></label>
                        <div class=\"row g-2\">
                            <div class=\"col-6\">
                                <label class=\"small text-muted\">Target</label>
                                <input type=\"number\" step=\"0.01\" class=\"form-control form-control-sm\" name=\"target_{{ c.code }}\" value=\"{{ defaults.get('target_' + c.code, 0) }}\" required>
                            </div>
                            <div class=\"col-6\">
                                <label class=\"small text-muted\">Bobot</label>
                                <input type=\"number\" step=\"0.01\" class=\"form-control form-control-sm\" name=\"weight_{{ c.code }}\" value=\"{{ defaults.get('weight_' + c.code, 1) }}\" required>
                            </div>
                        </div>
                    </div>
                    {% endfor %}

                    <button type=\"submit\" class=\"btn btn-success w-100\">Hitung Profile Matching</button>
                </form>
            </div>
        </div>
    </div>

    <div class=\"col-md-8\">
        {% if results is not none %}
        <div class=\"card mb-4\">
            <div class=\"card-header bg-success text-white\">
                <h5 class=\"mb-0\">Hasil Perankingan Profile Matching</h5>
            </div>
            <div class=\"card-body\">
                <div class=\"table-responsive\">
                    <table class=\"table table-striped table-hover\">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Alternatif</th>
                                <th>Total Skor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in results %}
                            <tr class=\"{{ 'table-success fw-bold' if loop.first else '' }}\">
                                <td>{{ row['Rank_PM']|int }}</td>
                                <td>{{ row['Alternatif'] }}</td>
                                <td>{{ "%.3f"|format(row['Total_PM']) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class=\"card\">
            <div class=\"card-header\">
                <h5 class=\"mb-0\">Visualisasi Skor PM</h5>
            </div>
            <div class=\"card-body\">
                <div id=\"chart\"></div>
            </div>
        </div>

        <script>
            var chartData = {{ chart_json | safe }};
            Plotly.newPlot('chart', chartData.data, chartData.layout);
        </script>
        {% else %}
        <div class=\"alert alert-info\">
            <h4 class=\"alert-heading\">Belum ada hasil!</h4>
            <p>Silakan atur target dan bobot di sebelah kiri lalu klik \"Hitung Profile Matching\".</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    "comparison.html": """{% extends 'base.html' %}
{% block content %}
<div class=\"row\">
    <div class=\"col-12\">
        <h2 class=\"mb-4\">Perbandingan Metode</h2>
        
        {% if error %}
        <div class=\"alert alert-warning\">
            <h4 class=\"alert-heading\">Data Belum Lengkap</h4>
            <p>{{ error }}</p>
            <hr>
            <p class=\"mb-0\">Silakan lakukan perhitungan di menu <strong>Profile Matching</strong> dan <strong>TOPSIS</strong> terlebih dahulu.</p>
        </div>
        {% else %}
        
        <div class=\"row mb-4\">
            <div class=\"col-md-6\">
                <div class=\"card h-100\">
                    <div class=\"card-header\">
                        <h5 class=\"mb-0\">Perbandingan Ranking</h5>
                    </div>
                    <div class=\"card-body\">
                        <div id=\"rankChart\"></div>
                    </div>
                </div>
            </div>
            <div class=\"col-md-6\">
                <div class=\"card h-100\">
                    <div class=\"card-header\">
                        <h5 class=\"mb-0\">Perbandingan Skor Normalisasi</h5>
                    </div>
                    <div class=\"card-body\">
                        <div id=\"scoreChart\"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class=\"card\">
            <div class=\"card-header\">
                <h5 class=\"mb-0\">Tabel Perbandingan Detail</h5>
            </div>
            <div class=\"card-body\">
                <div class=\"table-responsive\">
                    <table class=\"table table-bordered table-hover text-center align-middle\">
                        <thead class=\"table-dark\">
                            <tr>
                                <th rowspan=\"2\">Alternatif</th>
                                <th colspan=\"2\" class=\"bg-success\">Profile Matching</th>
                                <th colspan=\"2\" class=\"bg-primary\">TOPSIS</th>
                            </tr>
                            <tr>
                                <th class=\"bg-success text-white\">Skor</th>
                                <th class=\"bg-success text-white\">Rank</th>
                                <th class=\"bg-primary text-white\">Skor (V)</th>
                                <th class=\"bg-primary text-white\">Rank</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in comparison_data %}
                            <tr>
                                <td class=\"fw-bold text-start\">{{ row['Alternatif'] }}</td>
                                <td>{{ "%.3f"|format(row['Total_PM']) }}</td>
                                <td><span class=\"badge bg-success rounded-pill\">{{ row['Rank_PM']|int }}</span></td>
                                <td>{{ "%.4f"|format(row['V_TOPSIS']) }}</td>
                                <td><span class=\"badge bg-primary rounded-pill\">{{ row['Rank_TOPSIS']|int }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            var rankChartData = {{ rank_chart_json | safe }};
            Plotly.newPlot('rankChart', rankChartData.data, rankChartData.layout);

            var scoreChartData = {{ score_chart_json | safe }};
            Plotly.newPlot('scoreChart', scoreChartData.data, scoreChartData.layout);
        </script>
        {% endif %}
    </div>
</div>
{% endblock %}""",
}


# =========================
# Flask App & Algorithms
# =========================
app = Flask(__name__)
app.secret_key = "spk-secret-key"

# Use in-memory templates via DictLoader
app.jinja_loader = jinja2.DictLoader(TEMPLATES)


# Errors
class TopsisError(Exception):
    pass


class ProfileMatchingError(Exception):
    pass


# Algorithms
def _validate_matrix(matrix: List[List[float]], weights: List[float], impacts: List[str]) -> Tuple[int, int]:
    if not matrix or not isinstance(matrix, list):
        raise TopsisError("Matrix data tidak boleh kosong.")
    n = len(matrix)
    m = len(matrix[0]) if n > 0 else 0
    if n == 0 or m == 0:
        raise TopsisError("Matrix data tidak valid.")
    for row in matrix:
        if len(row) != m:
            raise TopsisError("Semua baris matrix harus memiliki jumlah kolom yang sama.")
        for val in row:
            if not isinstance(val, (int, float)):
                raise TopsisError("Semua nilai pada matrix harus angka.")
    if len(weights) != m:
        raise TopsisError("Jumlah bobot harus sama dengan jumlah kriteria.")
    if len(impacts) != m:
        raise TopsisError("Jumlah atribut (benefit/cost) harus sama dengan jumlah kriteria.")
    if any(w < 0 for w in weights):
        raise TopsisError("Bobot tidak boleh negatif.")
    impacts_clean = []
    for im in impacts:
        s = str(im).strip().lower()
        if s not in ("benefit", "cost"):
            raise TopsisError("Atribut kriteria harus 'benefit' atau 'cost'.")
        impacts_clean.append(s)
    return n, m


def topsis(matrix: List[List[float]], weights: List[float], impacts: List[str], labels: List[str]) -> List[Dict[str, float]]:
    n, m = _validate_matrix(matrix, weights, impacts)
    if len(labels) != n:
        raise TopsisError("Jumlah label alternatif harus sama dengan jumlah baris matrix.")

    col_sq_sums = [0.0] * m
    for j in range(m):
        col_sq_sums[j] = sum((matrix[i][j] ** 2 for i in range(n)))
        col_sq_sums[j] = math.sqrt(col_sq_sums[j]) if col_sq_sums[j] != 0 else 1.0

    norm = [[matrix[i][j] / col_sq_sums[j] for j in range(m)] for i in range(n)]

    total_w = sum(weights) or 1.0
    w_norm = [w / total_w for w in weights]
    v = [[norm[i][j] * w_norm[j] for j in range(m)] for i in range(n)]

    best = [0.0] * m
    worst = [0.0] * m
    for j in range(m):
        col_vals = [v[i][j] for i in range(n)]
        if impacts[j] == "benefit":
            best[j] = max(col_vals)
            worst[j] = min(col_vals)
        else:
            best[j] = min(col_vals)
            worst[j] = max(col_vals)

    d_plus = []
    d_minus = []
    for i in range(n):
        dp = math.sqrt(sum(((v[i][j] - best[j]) ** 2 for j in range(m))))
        dm = math.sqrt(sum(((v[i][j] - worst[j]) ** 2 for j in range(m))))
        d_plus.append(dp)
        d_minus.append(dm)

    results = []
    for i in range(n):
        denom = d_plus[i] + d_minus[i]
        vi = (d_minus[i] / denom) if denom != 0 else 0.0
        results.append({
            "Alternatif": labels[i],
            "D_Plus": d_plus[i],
            "D_Minus": d_minus[i],
            "V_TOPSIS": vi,
        })

    results_sorted = sorted(results, key=lambda r: r["V_TOPSIS"], reverse=True)
    for rank, row in enumerate(results_sorted, start=1):
        row["Rank_TOPSIS"] = rank
    return results_sorted


def _pm_gap_to_score(gap: int) -> float:
    table = {0: 5.0, 1: 4.5, -1: 4.0, 2: 4.0, -2: 3.5, 3: 3.0, -3: 2.5}
    if gap in table:
        return table[gap]
    return 2.0


def profile_matching(matrix: List[List[float]], targets: List[float], weights: List[float], labels: List[str]) -> List[Dict[str, float]]:
    if not matrix or not isinstance(matrix, list):
        raise ProfileMatchingError("Matrix data tidak boleh kosong.")
    n = len(matrix)
    m = len(matrix[0])
    if len(targets) != m or len(weights) != m:
        raise ProfileMatchingError("Panjang targets dan weights harus sama dengan jumlah kriteria.")
    if len(labels) != n:
        raise ProfileMatchingError("Jumlah label alternatif harus sama dengan jumlah baris matrix.")

    total_w = sum(weights) or 1.0
    w_norm = [w / total_w for w in weights]

    results = []
    for i in range(n):
        total_score = 0.0
        for j in range(m):
            gap = int(round(matrix[i][j] - targets[j]))
            score = _pm_gap_to_score(gap)
            total_score += score * w_norm[j]
        results.append({"Alternatif": labels[i], "Total_PM": total_score})

    results_sorted = sorted(results, key=lambda r: r["Total_PM"], reverse=True)
    for rank, row in enumerate(results_sorted, start=1):
        row["Rank_PM"] = rank
    return results_sorted


# =========================
# App State & Helpers
# =========================
# Persist data next to this script using an absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "spk_data.json")

STATE: Dict[str, any] = {
    "criteria": [
        {"code": "K1", "name": "Jenis kelas retinoid", "attr": "cost"},
        {"code": "K2", "name": "emollient", "attr": "benefit"},
        {"code": "K3", "name": "Dosis bahan aktif", "attr": "benefit"},
        {"code": "K4", "name": "Komposisi senyawa", "attr": "benefit"},
        {"code": "K5", "name": "Teknik formulasi", "attr": "cost"},
    ],
    "data": [
        {"Alternatif": "A1", "K1": 3.0, "K2": 4.0, "K3": 2.0, "K4": 3.0, "K5": 3.0},
        {"Alternatif": "A2", "K1": 5.0, "K2": 5.0, "K3": 4.0, "K4": 3.0, "K5": 2.0},
        {"Alternatif": "A3", "K1": 2.0, "K2": 4.0, "K3": 3.0, "K4": 4.0, "K5": 4.0},
        {"Alternatif": "A4", "K1": 4.0, "K2": 4.0, "K3": 4.0, "K4": 4.0, "K5": 3.0},
        {"Alternatif": "A5", "K1": 3.0, "K2": 4.0, "K3": 3.0, "K4": 3.0, "K5": 3.0},
    ],
    "topsis": None,
    "pm": None,
    "topsis_settings": {},
    "pm_settings": {},
}


def save_state():
    try:
        tmp_file = DATA_FILE + ".tmp"
        with open(tmp_file, 'w') as f:
            json.dump(STATE, f, indent=2)
        # Atomic replace to avoid partial writes
        os.replace(tmp_file, DATA_FILE)
    except Exception as e:
        print(f"Error saving state: {e}")


def load_state():
    global STATE
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                loaded = json.load(f)
                if "criteria" in loaded and "data" in loaded:
                    STATE.update(loaded)
        except Exception as e:
            print(f"Error loading state: {e}")


# Load data on startup
load_state()


def _matrix_from_state() -> Tuple[List[List[float]], List[str], List[dict]]:
    criteria_list = STATE["criteria"]
    labels = [row["Alternatif"] for row in STATE["data"]]
    # Matrix: rows=alternatives, cols=criteria
    matrix = []
    for row in STATE["data"]:
        matrix_row = []
        for c in criteria_list:
            # Default to 0.0 if key is missing or invalid
            val = float(row.get(c["code"], 0))
            matrix_row.append(val)
        matrix.append(matrix_row)
    
    return matrix, labels, criteria_list


# =========================
# Routes
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        new_data = []
        rows = len(STATE["data"])  # based on existing rows
        criteria_list = STATE["criteria"]
        for i in range(rows):
            alt_name = request.form.get(f"Alternatif_{i}", f"A{i+1}")
            if isinstance(alt_name, str):
                alt_name = alt_name.strip() or f"A{i+1}"
            row = {"Alternatif": alt_name}
            for c in criteria_list:
                code = c["code"]
                try:
                    val_str = request.form.get(f"{code}_{i}", "0")
                    val_clean = str(val_str).strip().replace(",", ".")
                    row[code] = float(val_clean)
                except ValueError:
                    row[code] = 0.0
            new_data.append(row)
        STATE["data"] = new_data
        save_state()
        flash("Perubahan disimpan.", "success")
        return redirect(url_for("index"))

    return render_template("index.html", criteria=STATE["criteria"], data=STATE["data"])


@app.route("/add_criteria", methods=["POST"])
def add_criteria():
    code = request.form.get("code", "").strip()
    name = request.form.get("name", "").strip()
    attr = request.form.get("attr", "benefit")

    if not code or not name:
        flash("Kode dan Nama Kriteria harus diisi!", "danger")
        return redirect(url_for("index"))
    
    # Check duplicate code
    if any(c["code"] == code for c in STATE["criteria"]):
        flash(f"Kriteria dengan kode {code} sudah ada!", "danger")
        return redirect(url_for("index"))

    # Add to structure
    STATE["criteria"].append({"code": code, "name": name, "attr": attr})
    
    # Add default 0 value to all existing data rows for this new criteria
    for row in STATE["data"]:
        row[code] = 0.0

    STATE["topsis"] = None
    STATE["pm"] = None
    save_state()

    flash("Kriteria berhasil ditambahkan.", "success")
    return redirect(url_for("index"))


@app.route("/delete_criteria/<int:i>")
def delete_criteria(i: int):
    if 0 <= i < len(STATE["criteria"]):
        deleted_c = STATE["criteria"].pop(i)
        code = deleted_c["code"]
        
        # Remove data from all rows
        for row in STATE["data"]:
            if code in row:
                del row[code]
        
        STATE["topsis"] = None
        STATE["pm"] = None

        save_state()
        flash(f"Kriteria {code} dihapus.", "warning")
    return redirect(url_for("index"))


@app.route("/add")
def add_row():
    idx = len(STATE["data"]) + 1
    # Generate unique default name if needed, but simple counter is fine for now
    row = {"Alternatif": f"A{idx}"}
    for c in STATE["criteria"]:
        row[c["code"]] = 0.0
    STATE["data"].append(row)
    save_state()
    flash("Baris alternatif baru ditambahkan.", "info")
    return redirect(url_for("index"))


@app.route("/delete/<int:i>")
def delete_row(i: int):
    if 0 <= i < len(STATE["data"]):
        STATE["data"].pop(i)
        save_state()
        flash("Baris dihapus.", "warning")
    return redirect(url_for("index"))


@app.route("/reset")
def reset_data():
    STATE["criteria"] = [
        {"code": "K1", "name": "Jenis kelas retinoid", "attr": "cost"},
        {"code": "K2", "name": "emollient", "attr": "benefit"},
        {"code": "K3", "name": "Dosis bahan aktif", "attr": "benefit"},
        {"code": "K4", "name": "Komposisi senyawa", "attr": "benefit"},
        {"code": "K5", "name": "Teknik formulasi", "attr": "cost"},
    ]
    STATE["data"] = [
        {"Alternatif": "A1", "K1": 3.0, "K2": 4.0, "K3": 2.0, "K4": 3.0, "K5": 3.0},
        {"Alternatif": "A2", "K1": 5.0, "K2": 5.0, "K3": 4.0, "K4": 3.0, "K5": 2.0},
        {"Alternatif": "A3", "K1": 2.0, "K2": 4.0, "K3": 3.0, "K4": 4.0, "K5": 4.0},
        {"Alternatif": "A4", "K1": 4.0, "K2": 4.0, "K3": 4.0, "K4": 4.0, "K5": 3.0},
        {"Alternatif": "A5", "K1": 3.0, "K2": 4.0, "K3": 3.0, "K4": 3.0, "K5": 3.0},
    ]
    STATE["topsis"] = None
    STATE["pm"] = None
    STATE["topsis_settings"] = {}
    STATE["pm_settings"] = {}
    save_state()
    flash("Data direset ke default (A1–A5).", "danger")
    return redirect(url_for("index"))


@app.route("/topsis", methods=["GET", "POST"])
def topsis_page():
    matrix, labels, criteria_list = _matrix_from_state()
    defaults = STATE.get("topsis_settings", {}).copy()

    if request.method == "POST":
        weights = []
        impacts = []
        current_settings = {}
        for c in criteria_list:
            code = c["code"]
            w_str = request.form.get(f"weight_{code}", "5")
            attr = request.form.get(f"attr_{code}", c["attr"]) # default from criteria definition
            try:
                w = float(w_str)
            except ValueError:
                w = 1.0
            weights.append(w)
            impacts.append(attr)
            current_settings[f"weight_{code}"] = w
            current_settings[f"attr_{code}"] = attr
        
        defaults.update(current_settings)
        STATE["topsis_settings"] = current_settings
        
        try:
            results = topsis(matrix, weights, impacts, labels)
            STATE["topsis"] = results
            save_state()
            flash("TOPSIS berhasil dihitung.", "success")
        except TopsisError as e:
            flash(str(e), "danger")

    results = STATE.get("topsis")
    chart_json = None
    if results:
        x = [r["Alternatif"] for r in results]
        y = [r["V_TOPSIS"] for r in results]
        chart_json = json.dumps({
            "data": [{"x": x, "y": y, "type": "bar", "marker": {"color": "#0d6efd"}}],
            "layout": {"title": "Nilai Preferensi TOPSIS", "yaxis": {"title": "V"}},
        })

    return render_template("topsis.html", criteria=criteria_list, defaults=defaults, results=results, chart_json=chart_json)


@app.route("/profile-matching", methods=["GET", "POST"])
def pm_page():
    matrix, labels, criteria_list = _matrix_from_state()
    defaults = STATE.get("pm_settings", {}).copy()
    results = STATE.get("pm")

    if request.method == "POST":
        targets = []
        weights = []
        current_settings = {}
        for c in criteria_list:
            code = c["code"]
            t_str = request.form.get(f"target_{code}", "0")
            w_str = request.form.get(f"weight_{code}", "1")
            try:
                t = float(t_str)
            except ValueError:
                t = 0.0
            try:
                w = float(w_str)
            except ValueError:
                w = 1.0
            targets.append(t)
            weights.append(w)
            current_settings[f"target_{code}"] = t
            current_settings[f"weight_{code}"] = w
        
        defaults.update(current_settings)
        STATE["pm_settings"] = current_settings
        try:
            results = profile_matching(matrix, targets, weights, labels)
            STATE["pm"] = results
            save_state()
            flash("Profile Matching berhasil dihitung.", "success")
        except ProfileMatchingError as e:
            flash(str(e), "danger")

    chart_json = None
    if results:
        x = [r["Alternatif"] for r in results]
        y = [r["Total_PM"] for r in results]
        chart_json = json.dumps({
            "data": [{"x": x, "y": y, "type": "bar", "marker": {"color": "#198754"}}],
            "layout": {"title": "Skor Profile Matching", "yaxis": {"title": "Skor"}},
        })

    return render_template("pm.html", criteria=criteria_list, defaults=defaults, results=results, chart_json=chart_json)


@app.route("/comparison")
def comparison_page():
    pm = STATE.get("pm")
    tp = STATE.get("topsis")
    error = None
    comparison_data = []
    rank_chart_json = None
    score_chart_json = None

    if not pm or not tp:
        error = "Hasil PM atau TOPSIS belum tersedia."
    else:
        pm_map = {r["Alternatif"]: r for r in pm}
        tp_map = {r["Alternatif"]: r for r in tp}
        alts = [row["Alternatif"] for row in STATE["data"]]
        for a in alts:
            p = pm_map.get(a)
            t = tp_map.get(a)
            if p and t:
                comparison_data.append({
                    "Alternatif": a,
                    "Total_PM": p["Total_PM"],
                    "Rank_PM": p["Rank_PM"],
                    "V_TOPSIS": t["V_TOPSIS"],
                    "Rank_TOPSIS": t["Rank_TOPSIS"],
                })
        x = [r["Alternatif"] for r in comparison_data]
        rank_chart_json = json.dumps({
            "data": [
                {"x": x, "y": [r["Rank_PM"] for r in comparison_data], "type": "bar", "name": "PM", "marker": {"color": "#198754"}},
                {"x": x, "y": [r["Rank_TOPSIS"] for r in comparison_data], "type": "bar", "name": "TOPSIS", "marker": {"color": "#0d6efd"}},
            ],
            "layout": {"barmode": "group", "title": "Perbandingan Ranking"}
        })
        score_chart_json = json.dumps({
            "data": [
                {"x": x, "y": [r["Total_PM"] for r in comparison_data], "type": "scatter", "mode": "lines+markers", "name": "PM", "line": {"color": "#198754"}},
                {"x": x, "y": [r["V_TOPSIS"] for r in comparison_data], "type": "scatter", "mode": "lines+markers", "name": "TOPSIS", "line": {"color": "#0d6efd"}},
            ],
            "layout": {"title": "Perbandingan Skor"}
        })

    return render_template("comparison.html", error=error, comparison_data=comparison_data, rank_chart_json=rank_chart_json, score_chart_json=score_chart_json)


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    print("Starting Flask server on http://0.0.0.0:8000 ...")
    try:
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except Exception as e:
        print("Server failed to start:", e)
