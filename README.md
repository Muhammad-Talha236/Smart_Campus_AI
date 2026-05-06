<div align="center">

# 🎓 Smart Campus AI

### Decision Support & Automation System

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-00C851?style=for-the-badge)
![No Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen?style=for-the-badge)

_Intelligent campus platform for students, instructors, and staff — powered by ANN, Logic/KB, CSP, and Graph Search. Pure Python. No installs._

</div>

---

## 🚀 Quick Start

```bash
cd smart_campus_ai
python main.py
```

> Requires **Python 3.7+** only. No external libraries needed.

---

## 📁 Project Structure

```
smart_campus_ai/
│
├── main.py                    ← Run this
│
├── data/
│   ├── campus_graph.py        ← Campus map (13 nodes, weighted + unweighted)
│   ├── encodings.py           ← ANN feature encodings
│   └── knowledge_base.py      ← Facts & rules for Logic/KB
│
├── modules/
│   ├── preprocessing.py       ← Input validation & normalization
│   ├── router.py              ← Pipeline selector
│   ├── ann_priority.py        ← Perceptron + MLP priority prediction
│   ├── logic_kb.py            ← Forward chaining inference engine
│   ├── csp_scheduler.py       ← Conflict-free slot & room assignment
│   ├── search_navigation.py   ← BFS, A*, UCS + 6 comparison algorithms
│   └── final_response.py      ← Aggregates all module outputs
│
└── utils/
    ├── display.py             ← Colored CLI output helpers
    └── validators.py          ← Input validation helpers
```

---

## 🔀 Request Types

| Type                     | Pipeline                                 |
| ------------------------ | ---------------------------------------- |
| `Navigation_Only`        | Search → Response                        |
| `Eligibility_Check`      | Logic/KB → Response                      |
| `Booking_or_Scheduling`  | Logic/KB → CSP → Response                |
| `Urgent_Service_Request` | ANN → Logic/KB → CSP → Search → Response |
| `Full_Service_Request`   | ANN → Logic/KB → CSP → Search → Response |

---

## 🧠 How It Works

**1. Input** — User enters name, role, request type, and relevant details via CLI.

**2. Preprocessing** — Fields are validated and normalized into a standard request object.

**3. Routing** — Router reads the request type and selects the correct module pipeline.

**4. ANN** _(if needed)_ — A 7-feature vector `[Role, ReqType, Severity, TimeSens, Crowd, Distance, Eligibility]` is passed through a Perceptron (binary) and MLP (multiclass) to predict priority.

**5. Logic/KB** _(if needed)_ — Forward chaining over 27 facts and 12 rules checks user eligibility and role permissions.

**6. CSP** _(if needed)_ — Assigns a conflict-free room and slot. Falls back to next available slot if preferred is taken.

**7. Search** _(if needed)_ — A\* finds the optimal weighted path. BFS used for unweighted. UCS as fallback.

**8. Response** — All module outputs are collected and displayed as one clean final response.

---

## 🗺️ Campus Locations

```
Main_Gate  •  Bus_Stop  •  Medical_Center  •  Hostel  •  Parking
Admin_Block  •  Student_Services  •  Exam_Hall  •  Seminar_Room
Library  •  AI_Lab  •  Science_Block  •  Cafeteria
```

---

## ⚠️ Common Errors

| Error                  | Fix                                                          |
| ---------------------- | ------------------------------------------------------------ |
| `python not found`     | Try `python3 main.py`                                        |
| `ModuleNotFoundError`  | Ensure `__init__.py` exists in `data/`, `modules/`, `utils/` |
| `No module named data` | Run from inside the `smart_campus_ai/` folder                |

---

<div align="center">
Pure Python &nbsp;·&nbsp; No pip install &nbsp;·&nbsp; CLI Based
</div>
