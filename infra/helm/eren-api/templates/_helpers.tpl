{{/*
Expand the name of this chart.
*/}}
{{- define "eren-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "eren-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create the service account name.
*/}}
{{- define "eren-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "eren-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create chart metadata.
*/}}
{{- define "eren-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "_" "-" | trunc 63 | trimSuffix "-" }}
{{- end }}
