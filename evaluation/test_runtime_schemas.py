from copy import deepcopy
import unittest

from jsonschema import ValidationError

from support import FoundationFixture
from tools.validate import ROOT, check_schema, read


class RuntimeSchemaTests(unittest.TestCase):
    def example(self, kind):
        return deepcopy(read(ROOT, f"schemas/{kind}.schema.json")["examples"][0])

    def check(self, kind, value):
        check_schema(ROOT, f"schemas/{kind}.schema.json", value)

    def running_task(self):
        task = self.example("task")
        task.update(status="RUNNING", task_version=2, execution_epoch=1,
                    leadership_epoch=1, assigned_agent_id="amo-research-agent-001",
                    assigned_node_id="amo-node-fixture-local", runtime_instance_id="run-fixture-001",
                    task_lease_expires_at="2026-11-01T20:00:00-08:00", attempt=1,
                    approval_ref="urn:amo:fixture:approval:001")
        return task

    def active_lease(self):
        lease = self.example("leadership_lease")
        lease.update(
            state="ACTIVE", leadership_epoch=1, lease_version=2,
            holder={"agent_id": "amo-ceo", "controller_instance_id": "run-fixture-001",
                    "node_id": "amo-node-fixture-local"},
            acquired_at="2026-11-01T19:50:00-08:00",
            last_renewed_at="2026-11-01T19:50:00-08:00",
            expires_at="2026-11-01T19:51:00-08:00",
            last_handover_event_ref="urn:amo:fixture:event:001",
            reconstruction_watermark="synthetic-watermark-001",
        )
        return lease

    def test_synthetic_examples_are_valid_without_registering_live_records(self):
        for kind in ("agent", "node", "task", "leadership_lease"):
            with self.subTest(kind=kind):
                self.check(kind, self.example(kind))

    def test_local_and_cloud_cannot_create_distinct_ceo_identities(self):
        for agent_id in ("amo-local-ceo", "amo-cloud-ceo"):
            agent = self.example("agent")
            agent["agent_id"] = agent_id
            with self.subTest(agent_id=agent_id), self.assertRaises(ValidationError):
                self.check("agent", agent)
        agent = self.example("agent")
        agent["role_type"] = "SUBAGENT"
        with self.assertRaises(ValidationError):
            self.check("agent", agent)

    def test_node_types_do_not_include_ceo_and_cannot_embed_credentials(self):
        node = self.example("node")
        for node_type in ("LOCAL", "CLOUD", "REMOTE_SERVER", "EDGE_DEVICE", "DEDICATED_COMPUTE_NODE"):
            node["node_type"] = node_type
            self.check("node", node)
        node["node_type"] = "LOCAL_CEO"
        with self.assertRaises(ValidationError):
            self.check("node", node)
        node["node_type"] = "LOCAL"
        node["personal_access_token"] = "synthetic-not-a-secret"
        with self.assertRaises(ValidationError):
            self.check("node", node)

    def test_assignment_requires_owner_and_positive_fences_and_lease(self):
        task = self.running_task()
        self.check("task", task)
        for field in ("assigned_agent_id", "assigned_node_id", "runtime_instance_id",
                      "task_lease_expires_at", "leadership_epoch"):
            broken = deepcopy(task)
            broken[field] = None
            with self.subTest(field=field), self.assertRaises(ValidationError):
                self.check("task", broken)
        task["execution_epoch"] = 0
        with self.assertRaises(ValidationError):
            self.check("task", task)

    def test_completion_requires_result_and_released_lease(self):
        task = self.running_task()
        task.update(status="COMPLETED", task_lease_expires_at=None)
        with self.assertRaises(ValidationError):
            self.check("task", task)
        task["result_ref"] = {
            "uri": "urn:amo:fixture:result:001", "sha256": "0" * 64, "media_type": "application/json",
        }
        self.check("task", task)
        task["task_lease_expires_at"] = "2026-11-01T20:00:00-08:00"
        with self.assertRaises(ValidationError):
            self.check("task", task)

    def test_unknown_and_nonidempotent_tasks_cannot_auto_retry_or_resume(self):
        for classification in ("UNKNOWN", "NON_IDEMPOTENT"):
            task = self.example("task")
            task["idempotency"]["classification"] = classification
            task["retry_policy"]["max_attempts"] = 2
            with self.subTest(classification=classification), self.assertRaises(ValidationError):
                self.check("task", task)
            task["retry_policy"]["max_attempts"] = 1
            task["resume_policy"] = "RESTART_SAFE"
            with self.assertRaises(ValidationError):
                self.check("task", task)

    def test_effect_tasks_need_idempotency_key_and_authorized_queue(self):
        task = self.example("task")
        task["idempotency"]["classification"] = "EXTERNAL_EFFECT"
        with self.assertRaises(ValidationError):
            self.check("task", task)
        task["idempotency"]["key"] = "synthetic-effect-001"
        task["status"] = "QUEUED"
        with self.assertRaises(ValidationError):
            self.check("task", task)
        task["approval_ref"] = "urn:amo:fixture:approval:001"
        self.check("task", task)

    def test_lease_holder_requires_epoch_expiration_and_reconstruction(self):
        lease = self.active_lease()
        self.check("leadership_lease", lease)
        for field, invalid in (("leadership_epoch", 0), ("expires_at", None),
                               ("reconstruction_watermark", None)):
            broken = deepcopy(lease)
            broken[field] = invalid
            with self.subTest(field=field), self.assertRaises(ValidationError):
                self.check("leadership_lease", broken)
        lease["holder"]["agent_id"] = "amo-cloud-ceo"
        with self.assertRaises(ValidationError):
            self.check("leadership_lease", lease)

    def test_references_and_timestamps_are_actually_format_checked(self):
        task = self.example("task")
        task["created_at"] = "not-a-time"
        with self.assertRaises(ValidationError):
            self.check("task", task)
        node = self.example("node")
        node["credential_profile_refs"] = ["not a URI"]
        with self.assertRaises(ValidationError):
            self.check("node", node)


class RuntimeSpecificationBoundaryTests(FoundationFixture):
    def test_specs_cannot_silently_grant_permissions_or_register_nodes(self):
        path = "governance/runtime_permissions.yaml"
        policy = self.read(path)
        policy["current_grants"] = ["synthetic-unapproved-grant"]
        self.put(path, policy)
        with self.assertRaisesRegex(ValueError, "cannot register nodes or grant"):
            self.check()

    def test_specs_cannot_enable_two_controllers(self):
        path = "governance/runtime_permissions.yaml"
        policy = self.read(path)
        policy["maximum_active_controllers"] = 2
        self.put(path, policy)
        with self.assertRaisesRegex(ValueError, "one active controller"):
            self.check()

    def test_invalid_embedded_examples_fail_repository_validation(self):
        path = "schemas/task.schema.json"
        schema = self.read(path)
        schema["examples"][0]["status"] = "RUNNING"
        self.put(path, schema)
        with self.assertRaises(ValidationError):
            self.check()
