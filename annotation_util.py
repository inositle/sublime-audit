import os
import json

def read_annotations_file(self, view):
	annotations = {}
	annotations['by_file'] = {}
	annotations['by_tag'] = {}

	folders = sublime.active_window().folders()
	if len(folders) == 1:
		proj_folder = folders[0]
		file_name = "annotations.json"
		annotations_file = os.path.join(proj_folder, file_name)
		if os.path.exists(annotations_file):
			f = open(annotations_file, "r")
			annotations = json.loads(f.read())
			f.close()

	return annotations_file, annotations