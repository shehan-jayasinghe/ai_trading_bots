{{- define "deriv-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "deriv-platform.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "deriv-platform.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "deriv-platform.labels" -}}
helm.sh/chart: {{ include "deriv-platform.chart" . }}
{{ include "deriv-platform.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "deriv-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ include "deriv-platform.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "deriv-platform.image" -}}
{{- $registry := .Values.image.registry -}}
{{- $repository := .repository -}}
{{- $tag := default .Values.image.tag .tag -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry $repository $tag -}}
{{- else -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end -}}
{{- end }}

{{- define "deriv-platform.postgresql.host" -}}
{{- printf "%s-postgresql" .Release.Name }}
{{- end }}

{{- define "deriv-platform.kafka.host" -}}
{{- printf "%s-kafka" .Release.Name }}
{{- end }}

{{- define "deriv-platform.postgresql.url" -}}
{{- $user := .Values.postgresql.auth.username -}}
{{- $db := .Values.postgresql.auth.database -}}
{{- $host := include "deriv-platform.postgresql.host" . -}}
{{- printf "postgresql+asyncpg://%s:$(POSTGRES_PASSWORD)@%s:5432/%s" $user $host $db -}}
{{- end }}

{{- define "deriv-platform.kafka.bootstrap" -}}
{{- printf "%s:9092" (include "deriv-platform.kafka.host" .) -}}
{{- end }}
