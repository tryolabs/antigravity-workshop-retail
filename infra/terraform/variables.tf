variable "project_id" {
  description = "Google Cloud Project ID hosting Retail Pulse Cloud Run, Vertex AI, and Gemini Enterprise."
  type        = string
}

variable "region" {
  description = "Primary Google Cloud region for Cloud Run and Artifact Registry."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run v2 service name for Retail Pulse (FastAPI + ADK + A2A + MCP)."
  type        = string
  default     = "retail-pulse-omnichannel"
}

variable "artifact_repo_name" {
  description = "Artifact Registry Docker repository name."
  type        = string
  default     = "retail-pulse-repo"
}

variable "image_tag" {
  description = "Container image tag deployed to Cloud Run."
  type        = string
  default     = "latest"
}

variable "gemini_enterprise_app_id" {
  description = "Gemini Enterprise (Discovery Engine) App/Engine ID for A2A agent registration."
  type        = string
  default     = "retail-pulse-gemini-enterprise-app"
}

variable "gemini_enterprise_location" {
  description = "Gemini Enterprise Discovery Engine location (global, us, or eu)."
  type        = string
  default     = "global"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run container instances."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run container instances."
  type        = number
  default     = 5
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated invocations (default false for enterprise zero-trust)."
  type        = bool
  default     = false
}
