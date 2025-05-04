import json

import pytest

from kiln_ai.adapters.eval.base_eval import BaseEval
from kiln_ai.datamodel import BasePrompt, DataSource, DataSourceType
from kiln_ai.datamodel.eval import Eval, EvalConfig, EvalOutputScore
from kiln_ai.datamodel.task import (
    RunConfigProperties,
    Task,
    TaskOutputRatingType,
    TaskRequirement,
    TaskRunConfig,
)


def test_score_schema_five_star():
    # Create an eval with a five-star score
    eval = Eval(
        name="Test Eval",
        eval_set_filter_id="tag::tag1",
        eval_configs_filter_id="tag::tag2",
        output_scores=[
            EvalOutputScore(
                name="Quality Score",
                instruction="Rate the quality",
                type=TaskOutputRatingType.five_star,
            ),
            EvalOutputScore(
                name="Overall Rating",
                instruction="The overall rating for the task output",
                type=TaskOutputRatingType.five_star,
            ),
        ],
    )

    schema_str = BaseEval.build_score_schema(eval)
    schema = json.loads(schema_str)

    # Check basic schema structure
    assert schema["type"] == "object"
    assert schema["required"] == ["quality_score", "overall_rating"]

    # Check score property, and that it's an enum of 1-5
    score_prop = schema["properties"]["quality_score"]
    assert score_prop["enum"] == [1, 2, 3, 4, 5]
    assert "Quality Score" in score_prop["title"]
    assert "Rate the quality" in score_prop["description"]
    assert "between 1 and 5" in score_prop["description"]

    # Check overall rating property, and that it's an enum of 1-5
    assert "overall_rating" in schema["properties"]
    overall = schema["properties"]["overall_rating"]
    assert overall["enum"] == [1, 2, 3, 4, 5]
    assert "Overall Rating" in overall["title"]
    assert "The overall rating for the task output" in overall["description"]
    assert "between 1 and 5" in overall["description"]
