# frozen_string_literal: true

require 'sketchup.rb'
require 'extensions.rb'

module StaadPrepBridge
  unless const_defined?(:EXTENSION)
    EXTENSION = SketchupExtension.new('STAAD Prep Bridge', 'staadprep/exporter')
    EXTENSION.description = 'Send analytical SketchUp edge geometry to STAAD Model Preprocessor.'
    EXTENSION.version = '0.1.0'
    EXTENSION.creator = 'STAAD Model Preprocessor'
    Sketchup.register_extension(EXTENSION, true)
  end
end
