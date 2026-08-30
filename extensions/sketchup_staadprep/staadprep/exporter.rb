# frozen_string_literal: true

require 'json'
require 'fileutils'
require 'sketchup.rb'

module StaadPrepBridge
  PREF_SECTION = 'STAAD Model Preprocessor'
  PREF_INBOX_KEY = 'SketchUpInbox'
  PROTOCOL_VERSION = 1
  LEGACY_INBOX_SUFFIX = File.join('artifacts', 'sketchup_bridge', 'inbox').tr('\\', '/')
  PORTABLE_INBOX_SUFFIX = File.join('Data', 'Inbox', 'SketchUp').tr('\\', '/')
  INBOX_SUFFIXES = [LEGACY_INBOX_SUFFIX, PORTABLE_INBOX_SUFFIX].freeze

  module_function

  def send_to_staad_prep
    inbox = configured_inbox || choose_inbox
    return unless inbox

    model = Sketchup.active_model
    payload = build_payload(model)
    output = write_atomic(inbox, payload)
    UI.messagebox("STAAD Prep geometry exported:\n#{output}")
    output
  rescue StandardError => e
    UI.messagebox("STAAD Prep export failed:\n#{e.message}")
    nil
  end

  def configured_inbox
    stored = Sketchup.read_default(PREF_SECTION, PREF_INBOX_KEY, nil)
    return File.expand_path(stored) if stored && valid_inbox_path?(stored)

    nil
  end

  def choose_inbox
    selected = UI.select_directory(title: 'Select STAAD Prep inbox')
    return nil unless selected

    expanded = File.expand_path(selected)
    unless valid_inbox_path?(expanded)
      UI.messagebox('Select either Data/Inbox/SketchUp or artifacts/sketchup_bridge/inbox.')
      return nil
    end

    Sketchup.write_default(PREF_SECTION, PREF_INBOX_KEY, expanded)
    expanded
  end

  def valid_inbox_path?(path)
    normalized = File.expand_path(path).tr('\\', '/')
    INBOX_SUFFIXES.any? { |suffix| normalized.end_with?(suffix) }
  end

  def bridge_html
    <<~HTML
      <!doctype html>
      <html lang="en">
      <head>
        <meta charset="utf-8">
        <style>
          :root { color-scheme: dark; }
          body {
            margin: 0;
            padding: 24px;
            background: #11161d;
            color: #d9e1ea;
            font-family: "Segoe UI", sans-serif;
            font-size: 14px;
          }
          h1 { margin: 0 0 12px; color: #ffffff; font-size: 22px; }
          p { margin: 8px 0; line-height: 1.5; }
          .note { color: #9fb0c1; }
          .panel {
            margin: 18px 0;
            padding: 12px 14px;
            background: #18212b;
            border: 1px solid #334354;
            border-radius: 6px;
          }
          .label { margin-bottom: 5px; color: #7faed1; font-weight: 700; }
          #inbox, #status { overflow-wrap: anywhere; }
          #status { color: #80d6a3; }
          .actions { display: flex; flex-wrap: wrap; gap: 9px; }
          button {
            min-height: 36px;
            padding: 7px 14px;
            background: #214d70;
            color: #ffffff;
            border: 1px solid #4da3ff;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
          }
          button.secondary { background: #202a35; border-color: #46586a; }
          button:hover { filter: brightness(1.12); }
        </style>
      </head>
      <body>
        <h1>STAAD Prep Bridge</h1>
        <p>Exports visible SketchUp edge geometry as Neutral JSON for STAAD Model Preprocessor.</p>
        <p class="note">This bridge transfers geometry only. It does not perform structural analysis or design calculations.</p>
        <div class="panel">
          <div class="label">STAAD Prep Inbox</div>
          <div id="inbox">Not configured</div>
        </div>
        <div class="actions">
          <button onclick="sketchup.export_geometry()">Export Geometry</button>
          <button class="secondary" onclick="sketchup.choose_inbox()">Choose Inbox...</button>
          <button class="secondary" onclick="sketchup.close_dialog()">Close</button>
        </div>
        <div class="panel">
          <div class="label">Last Result</div>
          <div id="status">Ready to export.</div>
        </div>
        <script>
          document.addEventListener('DOMContentLoaded', function () {
            sketchup.dialog_ready();
          });
          function setInbox(path) {
            document.getElementById('inbox').textContent = path;
          }
          function setStatus(message, isError) {
            const target = document.getElementById('status');
            target.textContent = message;
            target.style.color = isError ? '#ff8f8f' : '#80d6a3';
          }
        </script>
      </body>
      </html>
    HTML
  end

  def bridge_dialog
    return @bridge_dialog if @bridge_dialog

    dialog = UI::HtmlDialog.new(
      dialog_title: 'STAAD Prep Bridge',
      preferences_key: 'StaadPrepBridgeDialog',
      scrollable: false,
      resizable: true,
      width: 540,
      height: 470,
      style: UI::HtmlDialog::STYLE_DIALOG
    )
    dialog.set_html(bridge_html)
    dialog.add_action_callback('dialog_ready') do |_context|
      update_dialog_inbox
      update_dialog_status('Ready to export.')
    end
    dialog.add_action_callback('export_geometry') do |_context|
      output = send_to_staad_prep
      if output
        update_dialog_inbox
        update_dialog_status("Exported: #{File.basename(output)}")
      else
        update_dialog_status('Export cancelled or failed.', error: true)
      end
    end
    dialog.add_action_callback('choose_inbox') do |_context|
      selected = choose_inbox
      if selected
        update_dialog_inbox
        update_dialog_status('Inbox updated. Ready to export.')
      else
        update_dialog_status('Inbox unchanged.', error: true)
      end
    end
    dialog.add_action_callback('close_dialog') { |_context| dialog.close }
    dialog.set_on_closed { @bridge_dialog = nil }
    @bridge_dialog = dialog
  end

  def update_dialog_inbox
    return unless @bridge_dialog

    inbox = configured_inbox || 'Not configured'
    @bridge_dialog.execute_script("setInbox(#{JSON.generate(inbox)});")
  end

  def update_dialog_status(message, error: false)
    return unless @bridge_dialog

    @bridge_dialog.execute_script(
      "setStatus(#{JSON.generate(message.to_s)}, #{error ? 'true' : 'false'});"
    )
  end

  def show_bridge_dialog
    bridge_dialog.show
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
    final_path = next_output_path(inbox)
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

  def next_output_path(inbox, now = Time.now)
    base = "SP_#{now.strftime('%Y%m%d_%H%M%S')}"
    candidate = File.join(inbox, "#{base}.json")
    index = 2
    while File.exist?(candidate)
      candidate = File.join(inbox, format('%s_%02d.json', base, index))
      index += 1
    end
    candidate
  end

  unless file_loaded?(__FILE__)
    command = UI::Command.new('STAAD Prep Bridge') { show_bridge_dialog }
    command.menu_text = 'STAAD Prep Bridge...'
    command.tooltip = 'Export structural edge geometry to STAAD Model Preprocessor'
    command.status_bar_text = 'Send to STAAD Prep through the geometry bridge interface.'

    UI.menu('Extensions').add_item(command)
    toolbar = UI::Toolbar.new('STAAD Prep')
    toolbar.add_item(command)
    toolbar.show

    file_loaded(__FILE__)
  end
end
