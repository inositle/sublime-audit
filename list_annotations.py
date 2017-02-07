
import sublime
import sublime_plugin
import mdpopups
import time
import os
import json
import subprocess
import sys
import threading

annotation_thread = None

class ListAnnotationsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("running")
		folders = sublime.active_window().folders()
		if len(folders) == 1:
			proj_folder = folders[0]
			file_name = "annotations.json"
			self.annotations_file = os.path.join(proj_folder, file_name)
			if os.path.exists(self.annotations_file):
				f = open(self.annotations_file, "r")
				self.annotations = json.loads(f.read())
				f.close()
			else:
				self.annotations = {}
				self.annotations['by_file'] = {}
				self.annotations['by_tag'] = {}


		global annotation_thread
		if annotation_thread is None or not annotation_thread.isAlive():
			annotation_thread = AnnotationThread()
			annotation_thread.start()

		file_index = self.annotations['by_file']
		for ann_file in file_index:
			for region_start in file_index[ann_file]:
				text =  file_index[ann_file][region_start]['text']
				print("%s: %s" % (ann_file, text))

class AnnotationThread(threading.Thread):

	def run(self):
		folders = sublime.active_window().folders()
		if len(folders) == 1:
			proj_folder = folders[0]
			file_name = "annotations.json"
			self.annotations_file = os.path.join(proj_folder, file_name)
			if os.path.exists(self.annotations_file):
				f = open(self.annotations_file, "r")
				self.annotations = json.loads(f.read())
				f.close()
			else:
				self.annotations = {}
				self.annotations['by_file'] = {}
				self.annotations['by_tag'] = {}

			binfile = os.path.join(sublime.packages_path(), "sublime-audit", "lib", "qtable.py")

			args = [binfile  + " " + self.annotations_file + " " + folders[0] ]
			print(args)
			p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)

			while p.poll() is None:
				for lines in iter(p.stdout.readline, ""):
					if p.poll() is not None:
						break
					print(lines)
					if lines:
						lines = str(lines, 'utf-8')
						for l in lines.split("/n"):
							parts = str(l).split(",")
							print(parts[0])
							if len(parts) == 2:
								sublime.active_window().open_file(parts[0])
								view = sublime.active_window().active_view()
								target = view.text_point(int(parts[1]), 0)

								view.sel().clear()
								view.sel().add(sublime.Region(target))
								view.show(target)
		