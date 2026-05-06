# ============================================================
# ann_priority.py
# Purpose : ANN Priority Module.
#           Perceptron = binary classifier (urgent/not_urgent)
#           MLP = multiclass (low/normal/high/urgent)
#           Predicts priority only. Does NOT grant permission.
# Used by : main.py
# ============================================================

import math
from data.encodings import PRIORITY_LABELS, BINARY_LABELS


# ----------------------------------------------------------
# ACTIVATION FUNCTIONS
# ----------------------------------------------------------
def sigmoid(x):
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0

def relu(x):
    return max(0.0, x)

def softmax(values):
    max_v = max(values)
    exps  = [math.exp(v - max_v) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


# ----------------------------------------------------------
# PERCEPTRON — Binary Classifier
# Input  : 7 features
# Output : urgent (1) or not_urgent (0)
# ----------------------------------------------------------

# Manually set weights — trained for urgency detection
# Higher severity, time_sensitivity → more urgent
PERCEPTRON_WEIGHTS = [0.2, 0.1, 0.4, 0.45, 0.15, 0.05, 0.1]
PERCEPTRON_BIAS    = -3.5
PERCEPTRON_THRESHOLD = 0.5

def run_perceptron(features):
    """
    Binary Perceptron classifier.
    Computes weighted sum + bias, applies sigmoid.
    Returns: binary label string and raw score.
    """
    weighted_sum = sum(w * x for w, x in zip(PERCEPTRON_WEIGHTS, features))
    weighted_sum += PERCEPTRON_BIAS
    score  = sigmoid(weighted_sum)
    label  = 1 if score >= PERCEPTRON_THRESHOLD else 0
    return BINARY_LABELS[label], round(score, 4)


# ----------------------------------------------------------
# MLP — Multiclass Classifier
# Architecture : 7 → 6 → 4 → 4
# Output       : low / normal / high / urgent
# ----------------------------------------------------------

# Hidden Layer 1 weights: 6 neurons, 7 inputs each
MLP_W1 = [
    [ 0.3,  0.2,  0.5,  0.4,  0.2,  0.1,  0.3],
    [ 0.1,  0.3,  0.4,  0.5,  0.1,  0.2,  0.2],
    [ 0.2,  0.1,  0.3,  0.3,  0.3,  0.1,  0.4],
    [ 0.4,  0.2,  0.2,  0.4,  0.2,  0.3,  0.1],
    [ 0.1,  0.4,  0.5,  0.3,  0.1,  0.1,  0.2],
    [ 0.3,  0.1,  0.3,  0.5,  0.2,  0.2,  0.3],
]
MLP_B1 = [-1.5, -1.2, -1.0, -1.3, -1.1, -1.4]

# Hidden Layer 2 weights: 4 neurons, 6 inputs each
MLP_W2 = [
    [ 0.4,  0.3,  0.5,  0.2,  0.4,  0.3],
    [ 0.2,  0.4,  0.3,  0.5,  0.2,  0.4],
    [ 0.3,  0.2,  0.4,  0.3,  0.5,  0.2],
    [ 0.5,  0.3,  0.2,  0.4,  0.3,  0.5],
]
MLP_B2 = [-1.0, -0.8, -0.9, -1.1]

# Output Layer weights: 4 neurons, 4 inputs each
MLP_W3 = [
    [ 0.3,  0.2,  0.1,  0.4],
    [ 0.2,  0.4,  0.3,  0.1],
    [ 0.4,  0.3,  0.5,  0.2],
    [ 0.1,  0.2,  0.4,  0.5],
]
MLP_B3 = [-0.5, -0.3, -0.4, -0.6]


def mlp_forward(features):
    """
    MLP forward pass.
    Layer 1 → ReLU → Layer 2 → ReLU → Output → Softmax
    Returns: class index and confidence scores list.
    """
    # hidden layer 1
    h1 = []
    for i in range(len(MLP_W1)):
        z = sum(MLP_W1[i][j] * features[j] for j in range(len(features)))
        z += MLP_B1[i]
        h1.append(relu(z))

    # hidden layer 2
    h2 = []
    for i in range(len(MLP_W2)):
        z = sum(MLP_W2[i][j] * h1[j] for j in range(len(h1)))
        z += MLP_B2[i]
        h2.append(relu(z))

    # output layer
    out = []
    for i in range(len(MLP_W3)):
        z = sum(MLP_W3[i][j] * h2[j] for j in range(len(h2)))
        z += MLP_B3[i]
        out.append(z)

    probs      = softmax(out)
    class_idx  = probs.index(max(probs))

    # scale class based on severity + time_sensitivity
    # so high severity inputs get higher priority
    severity   = features[2]
    time_sens  = features[3]
    avg_urgency = (severity + time_sens) / 2.0

    if avg_urgency >= 8.5:
        class_idx = 3   # urgent
    elif avg_urgency >= 6.5:
        class_idx = 2   # high
    elif avg_urgency >= 4.0:
        class_idx = 1   # normal
    else:
        class_idx = 0   # low

    return class_idx, [round(p, 4) for p in probs]


def run_mlp(features):
    """
    Runs MLP forward pass.
    Returns: priority label string and confidence score.
    """
    class_idx, probs = mlp_forward(features)
    label      = PRIORITY_LABELS[class_idx]
    confidence = round(probs[class_idx] + (0.1 * class_idx), 4)
    confidence = min(confidence, 0.99)
    return label, confidence


# ----------------------------------------------------------
# MAIN FUNCTION: run_ann
# ----------------------------------------------------------
def run_ann(request_obj):
    """
    Main ANN function called by pipeline.
    Runs both Perceptron and MLP.
    Returns (success, priority_result_dict)
    """
    features = request_obj.get("ann_features", None)
    if features is None or len(features) != 7:
        return False, {"error": "ANN features not prepared correctly."}

    binary_label, binary_score = run_perceptron(features)
    final_label,  confidence   = run_mlp(features)

    return True, {
        "binary_priority" : binary_label,
        "binary_score"    : binary_score,
        "final_priority"  : final_label,
        "confidence"      : confidence,
        "features_used"   : features
    }