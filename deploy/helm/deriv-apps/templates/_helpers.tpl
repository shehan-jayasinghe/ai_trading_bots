{{- define "deriv-apps.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "deriv-apps.fullname" -}}
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

{{- define "deriv-apps.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "deriv-apps.labels" -}}
helm.sh/chart: {{ include "deriv-apps.chart" . }}
{{ include "deriv-apps.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "deriv-apps.selectorLabels" -}}
app.kubernetes.io/name: {{ include "deriv-apps.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "deriv-apps.image" -}}
{{- $registry := .Values.image.registry -}}
{{- $repository := .repository -}}
{{- $tag := default .Values.image.tag .tag -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry $repository $tag -}}
{{- else -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end -}}
{{- end }}

{{- define "deriv-apps.postgresql.url" -}}
{{- $user := .Values.externalServices.postgresql.username -}}
{{- $db := .Values.externalServices.postgresql.database -}}
{{- $host := .Values.externalServices.postgresql.host -}}
{{- $port := .Values.externalServices.postgresql.port -}}
{{- printf "postgresql+asyncpg://%s:$(POSTGRES_PASSWORD)@%s:%v/%s" $user $host $port $db -}}
{{- end }}

{{- define "deriv-apps.kafka.bootstrap" -}}
{{- printf "%s:%v" .Values.externalServices.kafka.host .Values.externalServices.kafka.port -}}
{{- end }}

{{- define "deriv-apps.postgresql.prismaUrl" -}}
{{- $user := .Values.externalServices.postgresql.username -}}
{{- $db := .Values.externalServices.postgresql.database -}}
{{- $host := .Values.externalServices.postgresql.host -}}
{{- $port := .Values.externalServices.postgresql.port -}}
{{- printf "postgresql://%s:$(POSTGRES_PASSWORD)@%s:%v/%s" $user $host $port $db -}}
{{- end }}

{{- define "deriv-apps.secretEnvFrom" -}}
envFrom:
  - secretRef:
      name: {{ .Values.secrets.existingSecret }}
{{- end }}
