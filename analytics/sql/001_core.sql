CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS channels (
  channel_id text PRIMARY KEY,
  display_name text,
  authorization_mode text NOT NULL CHECK (authorization_mode IN ('owner_oauth','public_only')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS source_media (
  source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,
  external_id text NOT NULL,
  channel_id text REFERENCES channels(channel_id),
  source_url text,
  title text,
  published_at timestamptz,
  duration_ms bigint CHECK (duration_ms > 0),
  original_language text,
  rights_status text NOT NULL DEFAULT 'unverified',
  metadata jsonb NOT NULL DEFAULT '{}',
  UNIQUE(provider, external_id)
);

CREATE TABLE IF NOT EXISTS clips (
  clip_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  primary_source_id uuid REFERENCES source_media(source_id),
  status text NOT NULL DEFAULT 'candidate',
  created_at timestamptz NOT NULL DEFAULT now(),
  candidate_reason text
);

CREATE TABLE IF NOT EXISTS clip_versions (
  clip_version_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clip_id uuid NOT NULL REFERENCES clips(clip_id) ON DELETE CASCADE,
  version_number integer NOT NULL CHECK (version_number > 0),
  final_duration_ms bigint NOT NULL CHECK (final_duration_ms > 0),
  output_language text NOT NULL,
  width integer NOT NULL CHECK (width > 0),
  height integer NOT NULL CHECK (height > 0),
  render_uri text,
  render_sha256 text,
  edit_manifest jsonb NOT NULL DEFAULT '{}',
  hook_type text,
  narrative_structure text,
  hook_text text,
  production_cost_usd numeric(12,4),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(clip_id, version_number)
);

CREATE TABLE IF NOT EXISTS clip_spans (
  clip_version_id uuid NOT NULL REFERENCES clip_versions(clip_version_id) ON DELETE CASCADE,
  span_order integer NOT NULL,
  source_id uuid NOT NULL REFERENCES source_media(source_id),
  source_start_ms bigint NOT NULL CHECK (source_start_ms >= 0),
  source_end_ms bigint NOT NULL,
  output_start_ms bigint NOT NULL CHECK (output_start_ms >= 0),
  output_end_ms bigint NOT NULL,
  playback_rate numeric(8,4) NOT NULL DEFAULT 1 CHECK (playback_rate > 0),
  PRIMARY KEY(clip_version_id, span_order),
  CHECK (source_end_ms > source_start_ms),
  CHECK (output_end_ms > output_start_ms)
);

CREATE TABLE IF NOT EXISTS publications (
  publication_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clip_version_id uuid NOT NULL REFERENCES clip_versions(clip_version_id),
  channel_id text NOT NULL REFERENCES channels(channel_id),
  youtube_video_id text UNIQUE,
  published_at timestamptz,
  content_format text NOT NULL DEFAULT 'unknown',
  status text NOT NULL DEFAULT 'planned',
  language text,
  topic text,
  submitted_title text,
  submitted_thumbnail_sha256 text,
  packaging_manifest jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS packaging_events (
  packaging_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  publication_id uuid NOT NULL REFERENCES publications(publication_id) ON DELETE CASCADE,
  effective_at timestamptz NOT NULL,
  observed_at timestamptz NOT NULL DEFAULT now(),
  title text,
  thumbnail_uri text,
  thumbnail_sha256 text
);

CREATE TABLE IF NOT EXISTS analytics_daily (
  publication_id uuid NOT NULL REFERENCES publications(publication_id) ON DELETE CASCADE,
  analytics_day date NOT NULL,
  report_family text NOT NULL,
  views bigint,
  engaged_views bigint,
  estimated_minutes_watched numeric(16,4),
  average_view_duration_seconds numeric(12,4),
  average_view_percentage numeric(12,4),
  likes bigint,
  comments bigint,
  shares bigint,
  subscribers_gained bigint,
  subscribers_lost bigint,
  estimated_revenue_usd numeric(14,6),
  PRIMARY KEY(publication_id, analytics_day, report_family)
);

CREATE TABLE IF NOT EXISTS retention_reports (
  retention_report_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  publication_id uuid NOT NULL REFERENCES publications(publication_id) ON DELETE CASCADE,
  period_start date NOT NULL,
  period_end date NOT NULL,
  fetched_at timestamptz NOT NULL DEFAULT now(),
  CHECK (period_end >= period_start)
);

CREATE TABLE IF NOT EXISTS retention_points (
  retention_report_id uuid NOT NULL REFERENCES retention_reports(retention_report_id) ON DELETE CASCADE,
  elapsed_ratio numeric(7,6) NOT NULL CHECK (elapsed_ratio BETWEEN 0 AND 1),
  audience_watch_ratio numeric(12,6),
  relative_retention_performance numeric(7,6),
  PRIMARY KEY(retention_report_id, elapsed_ratio)
);

CREATE TABLE IF NOT EXISTS content_economics (
  publication_id uuid PRIMARY KEY REFERENCES publications(publication_id) ON DELETE CASCADE,
  attributable_external_income_usd numeric(14,6),
  editing_cost_usd numeric(14,6),
  license_cost_usd numeric(14,6),
  compute_cost_usd numeric(14,6),
  promotion_cost_usd numeric(14,6),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS source_media_channel_date ON source_media(channel_id,published_at DESC);
CREATE INDEX IF NOT EXISTS publication_channel_date ON publications(channel_id,published_at DESC);
CREATE INDEX IF NOT EXISTS analytics_day_lookup ON analytics_daily(analytics_day,report_family);
