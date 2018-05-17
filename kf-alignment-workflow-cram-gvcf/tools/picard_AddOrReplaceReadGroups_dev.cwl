cwlVersion: v1.0
class: CommandLineTool
id: picard_AddOrReplaceReadGroups
requirements:
  - class: DockerRequirement
    dockerPull: 'kfdrc/picard:2.8.3'
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 8000
baseCommand: [java, -Xms4000m, -jar, /picard.jar, AddOrReplaceReadGroups]
arguments:
  - position: 1
    shellQuote: false
    valueFrom: >-
      OUTPUT=$(inputs.base_file_name).AddOrReplaceReadGroups.cram
      RGSM=$(inputs.base_file_name)
      RGID=
      RGLB=
      RGPL=
      RGPU=
inputs:
  input_cram:
    type: File
    inputBinding:
      prefix: INPUT=
      separate: false
  base_file_name: string
outputs: 
  output_AddOrReplaceReadGroups_bam:
    type: File
    outputBinding:
      glob: '*.cram'
