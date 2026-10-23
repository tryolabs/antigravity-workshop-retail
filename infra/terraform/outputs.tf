output "cloud_run_service_url" {
  description = "Base HTTPS URL of the deployed Retail Pulse Cloud Run v2 service."
  value       = google_cloud_run_v2_service.retail_pulse_service.uri
}

output "a2a_agent_card_url" {
  description = "A2A Agent Discovery Card endpoint (`/.well-known/agent.json`) for Gemini Enterprise registration."
  value       = "${google_cloud_run_v2_service.retail_pulse_service.uri}/.well-known/agent.json"
}

output "a2a_jsonrpc_endpoint" {
  description = "A2A JSON-RPC 2.0 Task endpoint (`/api/v1/a2a`) for multi-agent invocation."
  value       = "${google_cloud_run_v2_service.retail_pulse_service.uri}/api/v1/a2a"
}

output "artifact_registry_repository" {
  description = "Full Artifact Registry Docker repository path."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.retail_pulse_repo.repository_id}"
}

output "service_account_email" {
  description = "Least-privilege runtime Service Account email for Retail Pulse Cloud Run."
  value       = google_service_account.retail_pulse_sa.email
}

output "gemini_enterprise_agent_registration_endpoint" {
  description = "Discovery Engine REST API endpoint used to register the Retail Pulse A2A Agent in Gemini Enterprise."
  value       = "https://discoveryengine.googleapis.com/v1alpha/projects/${var.project_id}/locations/${var.gemini_enterprise_location}/collections/default_collection/engines/${var.gemini_enterprise_app_id}/assistants/default_assistant/agents"
}
