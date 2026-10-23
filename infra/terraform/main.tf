locals {
  required_googleapis = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudaicompanion.googleapis.com",
    "discoveryengine.googleapis.com",
    "logging.googleapis.com",
  ]
  container_image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/${var.service_name}:${var.image_tag}"
}

resource "google_project_service" "required_apis" {
  for_each           = toset(local.required_googleapis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "retail_pulse_repo" {
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "Docker repository for Retail Pulse Omnichannel FastAPI, ADK & A2A Agent service"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

resource "google_service_account" "retail_pulse_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Retail Pulse ADK & A2A Cloud Run Service Account"
  description  = "Least-privilege runtime identity for Retail Pulse on Cloud Run with Vertex AI and Cloud Logging access."

  depends_on = [google_project_service.required_apis]
}

resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.retail_pulse_sa.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.retail_pulse_sa.email}"
}

resource "google_cloud_run_v2_service" "retail_pulse_service" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.retail_pulse_sa.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = local.container_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }

      env {
        name  = "GEMINI_ENTERPRISE_APP_ID"
        value = var.gemini_enterprise_app_id
      }

      startup_probe {
        http_get {
          path = "/api/v1/health"
          port = 8080
        }
        initial_delay_seconds = 3
        period_seconds        = 5
        failure_threshold     = 6
      }
    }
  }

  depends_on = [
    google_artifact_registry_repository.retail_pulse_repo,
    google_project_iam_member.aiplatform_user,
    google_project_iam_member.log_writer,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = google_cloud_run_v2_service.retail_pulse_service.project
  location = google_cloud_run_v2_service.retail_pulse_service.location
  name     = google_cloud_run_v2_service.retail_pulse_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
