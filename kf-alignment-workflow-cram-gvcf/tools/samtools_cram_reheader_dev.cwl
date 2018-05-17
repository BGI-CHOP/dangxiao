cwlVersion: v1.0
class: CommandLineTool
id: samtools_cram_reheader
requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 4000
  - class: DockerRequirement
    dockerPull: 'kfdrc/samtools:1.8-dev'
baseCommand: [samtools, view]
arguments:
  - position: 1
    shellQuote: false
    valueFrom: >-
      -H $(inputs.input_cram.path) | sed  "/^@RG/s/SM:.*$/SM:$(inputs.base_file_name)/g" | samtools reheader - $(inputs.input_cram.path) > $(inputs.input_cram.nameroot).reheader.cram
#      && samtools index $(inputs.input_cram.nameroot).reheader.cram
inputs:
  input_cram: File
  base_file_name: string
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.cram'
    secondaryFiles: [.crai]
