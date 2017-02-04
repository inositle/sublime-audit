import sublime
import sublime_plugin
import mdpopups
import os
import json
import re


class AnnotateCommand(sublime_plugin.TextCommand):
	# TODO:
	#	database (json is for a lazy prototype)
	#	annotation timestamps
	# 	standalone ui to browse annotations
	annotations = None 
	annotations_file = None

	def annotation_region_from_pos(self, c):
		(row, col) = self.view.rowcol(c.begin())
		f = self.view.file_name()
		line_start = self.view.line(self.view.text_point(row-1, 0)).b
		location = sublime.Region(line_start, line_start)
		return f, line_start, location

	def create_annotation(self, f, text, tags, location, line_start):
		sline = str(line_start)
		self.annotations['by_file'][f][sline] = {}
		self.annotations['by_file'][f][sline]['tag_list'] = tags
		self.annotations['by_file'][f][sline]['text'] = text	
		html = '<style>p{color: #f4dc42}</style><p align="left">%s</p>' % text
		pid = mdpopups.add_phantom(self.view, "annotation", location, html, 
			                       layout=sublime.LAYOUT_BELOW)
		self.annotations['by_file'][f][sline]['pid'] = pid

	def update_annotation(self, f, text, tags, location, line_start):

		# Update tag index
		sline = str(line_start)
		tag_list = self.annotations['by_file'][f][sline]['tag_list']
		for t in tag_list:
			if t not in tags:
				# Remove tag index
				self.annotations['by_tag'][t].remove([f, line_start])

		# Update file index
		self.annotations['by_file'][f][sline]['tag_list'] = tags
		self.annotations['by_file'][f][sline]['text'] = text

		# Remove old phantom
		pid = self.annotations['by_file'][f][sline]['pid']
		mdpopups.erase_phantom_by_id(self.view, pid)

		# If the annotation was cleared, remove it. Otherwise add a new phantom
		html = '<style>p{color: #f4dc42}</style><p align="left">%s</p>' % text
		if text is not None and text.strip() is not "":
			pid = mdpopups.add_phantom(self.view, "annotation", location, html, 
				                       layout=sublime.LAYOUT_BELOW)
			self.annotations['by_file'][f][str(sline)]['pid'] = pid
		else:
			self.annotations['by_file'][f].pop(sline)

	def handle_input(self, text):
		print(text)
		tokens = text.split()
		tags = []
		for t in tokens:
			if t.startswith("#") and len(t) > 1:
				if t not in self.annotations['by_tag']:
					self.annotations['by_tag'][t] = []
				tags.append(t)

		pos = self.view.sel()
		for c in pos:
			f, line_start, location = self.annotation_region_from_pos(c)
			
			if f not in self.annotations['by_file']:
				self.annotations['by_file'][f] = {}

			exists = False
			if str(line_start) in self.annotations['by_file'][f]:
				exists = True

			for t in tags:
				if [f, line_start] not in self.annotations['by_tag'][t]:
					self.annotations['by_tag'][t].append([f, line_start])

			if not exists:
				self.create_annotation(f, text, tags, location, line_start)
			else:
				self.update_annotation(f, text, tags, location, line_start)
				
		ann = open(self.annotations_file, "w+")
		ann.write(json.dumps(self.annotations))
		ann.close()

	def setup_annotations(self):
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

		else:
			#todo
			pass

	def add_all_phantoms(self):
		if self.view.file_name() not in self.annotations['by_file']:
			return

		html = '<style>p{color: #f4dc42}</style><p align="left">%s</p>' % text
		file_name = self.view.file_name()
		for loc in self.annotations['by_file'][file_name]:
			int_loc = int(loc)
			region = sublime.Region(int_loc, int_loc)
			text = self.annotations['by_file'][file_name][loc]['text']
			pid = mdpopups.add_phantom(self.view, "hi", region, html, 
				                       layout=sublime.LAYOUT_BELOW)
			self.annotations['by_file'][file_name][loc]['pid'] = pid

	def file_load_event(self):
		if self.annotations is None:
			self.setup_annotations()
		self.add_all_phantoms()

	def run(self, edit):
		if self.annotations is None:
			self.setup_annotations()

		f = self.view.file_name()
		
		pos = self.view.sel()
		display_text = ""
		for c in pos:
			(row, col) = self.view.rowcol(c.begin())
			location_start = self.view.line(self.view.text_point(row-1, 0)).b
			location = sublime.Region(location_start, location_start)
			file_index = self.annotations['by_file']
			if f in file_index and str(location_start) in file_index[f]:
				display_text = file_index[f][str(location_start)]['text']
			
		self.view.window().show_input_panel("Add Annotation", display_text, 
							                self.handle_input, None, None)


class AnnotationListener(sublime_plugin.EventListener):

	def on_load(self, view):
		# excludes .py for development
		if not view.file_name().endswith(".py"):
			view.set_read_only(True)
		a = AnnotateCommand(view)
		a.file_load_event()