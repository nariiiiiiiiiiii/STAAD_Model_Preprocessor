# frozen_string_literal: true

require 'json'
require 'fileutils'
require 'securerandom'
require 'sketchup.rb'

module StaadPrepBridge
  PREF_SECTION = 'STAAD Model Preprocessor'
  PREF_INBOX_KEY = 'SketchUpInbox'
  PROTOCOL_VERSION = 1
  INBOX_SUFFIX = File.join('artifacts', 'sketchup_bridge', 'inbox').tr('\\', '/')

  module_function

  def send_to_staad_prep
    inbox = configured_inbox
    return unless inbox

    model = Sketchup.active_model
    payload = build_payload(model)
    output = write_atomic(inbox, payload)
    UI.messagebox("STAAD Prep geometry exported:\n#{output}")
  rescue StandardError => e
    UI.messagebox("STAAD Prep export failed:\n#{e.message}")
  end

  def configured_inbox
    stored = Sketchup.read_default(PREF_SECTION, PREF_INBOX_KEY, nil)
    return File.expand_path(stored) if stored && valid_inbox_path?(stored)

    selected = UI.select_directory(title: 'Select STAAD Prep artifacts/sketchup_bridge/inbox')
    return nil unless selected

    expanded = File.expand_path(selected)
    unless valid_inbox_path?(expanded)
      UI.messagebox('Select the project-local artifacts/sketchup_bridge/inbox folder.')
      return nil
    end

    Sketchup.write_default(PREF_SECTION, PREF_INBOX_KEY, expanded)
    expanded
  end

  def valid_inbox_path?(path)
    normalized = File.expand_path(path).tr('\\', '/')
    normalized.end_with?(INBOX_SUFFIX)
  end

  def build_payload(model)
    segments = []
    groups = []
    tags = []
    warnings = []
    identity = Geom::Transformation.new

    walk_entities(model.entities, identity, [], [], [], segments, groups, tags)

    source_file = model.path.to_s
    if source_file.empty?
      source_file = model.title.to_s.empty? ? 'Untitled.skp' : model.title.to_s
      warnings << 'SketchUp model has not been saved; source_file is a display name only.'
    end

    {
      'protocol_version' => PROTOCOL_VERSION,
      'source_file' => source_file,
      # SketchUp Length#to_f uses the API's internal inch coordinate values.
      # Keep that numeric unit explicit and let the Python T06 layer convert once.
      'source_unit' => "in",
      'source_axis' => 'Z-UP',
      'points' => [],
      'segments' => segments,
      'groups' => groups.uniq,
      'tags' => tags.uniq,
      'warnings' => warnings,
      'model_length_unit' => model.options['UnitsOptions']['LengthUnit']
    }
  end

  def walk_entities(entities, parent_transform, group_path, component_path, ref_path, segments, groups, tags)
    entities.each do |entity|
      case entity
      when Sketchup::Edge
        append_edge(entity, parent_transform, group_path, component_path, ref_path, segments, tags)
      when Sketchup::Group
        name = entity_name(entity.name, 'Group', entity.persistent_id)
        groups << name
        child_transform = parent_transform * entity.transformation
        walk_entities(
          entity.entities,
          child_transform,
          group_path + [name],
          component_path,
          ref_path + ["group:#{entity.persistent_id}"],
          segments,
          groups,
          tags
        )
      when Sketchup::ComponentInstance
        definition = entity.definition
        preferred = entity.name.to_s.empty? ? definition.name : entity.name
        name = entity_name(preferred, 'Component', entity.persistent_id)
        child_transform = parent_transform * entity.transformation
        walk_entities(
          definition.entities,
          child_transform,
          group_path,
          component_path + [name],
          ref_path + ["component:#{entity.persistent_id}"],
          segments,
          groups,
          tags
        )
      end
    end
  end

  def append_edge(edge, transform, group_path, component_path, ref_path, segments, tags)
    world_start = transform * edge.start.position
    world_end = transform * edge.end.position
    tag = edge.layer ? edge.layer.name.to_s : nil
    tags << tag if tag && !tag.empty?

    segments << {
      'start' => point_array(world_start),
      'end' => point_array(world_end),
      'source_ref' => (ref_path + ["edge:#{edge.persistent_id}"]).join('/'),
      'tag' => tag,
      'group_path' => group_path,
      'component_path' => component_path
    }
  end

  def point_array(point)
    [point.x.to_f, point.y.to_f, point.z.to_f]
  end

  def entity_name(value, fallback_prefix, persistent_id)
    text = value.to_s.strip
    text.empty? ? "#{fallback_prefix} #{persistent_id}" : text
  end

  def write_atomic(inbox, payload)
    FileUtils.mkdir_p(inbox)
    token = SecureRandom.hex(6)
    stamp = Time.now.strftime('%Y%m%d-%H%M%S')
    final_path = File.join(inbox, "staadprep-#{stamp}-#{token}.json")
    temp_path = "#{final_path}.tmp"

    File.open(temp_path, 'wb') do |file|
      file.write(JSON.pretty_generate(payload))
      file.flush
      file.fsync
    end
    File.rename(temp_path, final_path)
    final_path
  ensure
    File.delete(temp_path) if defined?(temp_path) && temp_path && File.exist?(temp_path)
  end

  unless file_loaded?(__FILE__)
    command = UI::Command.new('Send to STAAD Prep') { send_to_staad_prep }
    command.menu_text = 'Send to STAAD Prep'
    command.tooltip = 'Export structural edge geometry to STAAD Model Preprocessor'
    command.status_bar_text = 'Send SketchUp edge geometry to the project-local STAAD Prep inbox.'

    UI.menu('Extensions').add_item(command)
    toolbar = UI::Toolbar.new('STAAD Prep')
    toolbar.add_item(command)
    toolbar.show

    file_loaded(__FILE__)
  end
end
