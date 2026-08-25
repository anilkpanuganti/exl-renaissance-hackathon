import json
from prototype.src import validate as v


def test_entity_grounding_accuracy_all_grounded():
    analysis = {"tables": ["A", "B"]}
    source_sql = "select * from A join B on ..."
    res = v.entity_grounding_accuracy(analysis, source_sql)
    assert res["score"] == 1.0
    assert res["ungrounded"] == []


def test_entity_grounding_accuracy_some_ungrounded():
    analysis = {"tables": ["A", "C"]}
    source_sql = "select * from A"
    res = v.entity_grounding_accuracy(analysis, source_sql)
    assert res["score"] == 0.5
    assert "C" in res["ungrounded"]


def test_business_rule_coverage():
    analysis = {"business_rules": [{"name": "Promo Shrink", "description": "reduce by 10%"}]}
    ground_truth = {"business_rules": [{"id": "BR-1", "name": "Promotional Shrinkage"}, {"id": "BR-2", "name": "Other Rule"}]}
    res = v.business_rule_coverage(analysis, ground_truth)
    # one of two ground truth rules matched heuristically
    assert res["total_ground_truth_rules"] == 2
    assert isinstance(res["score"], float)


def test_ambiguity_flag_recall():
    analysis = {"business_rules": [{"id": "BR-1", "ambiguity_flag": True}, {"id": "BR-2"} ]}
    ground_truth = {"business_rules": [{"id": "BR-1", "ambiguity_flag": True}, {"id": "BR-3", "ambiguity_flag": True}]}
    res = v.ambiguity_flag_recall(analysis, ground_truth)
    assert res["expected"] == 2
    # only one ambiguous flagged by AI
    assert res["flagged_by_ai"] == 1
