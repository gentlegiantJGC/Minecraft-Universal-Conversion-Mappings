from PyMCTCompiler.compile import save_json, load_file, isfile, isdir, listdir, merge_map, blocks_from_server, compiled_dir, DiskBuffer
from PyMCTCompiler import primitives

"""
Summary


"""


def to_snbt(nbt_type, value):
	if nbt_type == 'byte':
		return f'{value}b'
	elif nbt_type == 'short':
		return f'{value}s'
	elif nbt_type == 'int':
		return f'{value}'
	elif nbt_type == 'long':
		return f'{value}l'
	elif nbt_type == 'float':
		return f'{value}f'
	elif nbt_type == 'double':
		return f'{value}d'
	elif nbt_type == 'string':
		return f'"{value}"'
	else:
		raise NotImplemented


def main(version_name: str, version_str: str):
	"""Custom compiler for the Java 1.13+ versions.

	:param version_name: The folder name of the version being compiled
	:param version_str: The string of the version number exactly as it appears in the version manifest
	"""

	if isfile(f'{version_name}/block_palette.json'):
		output = DiskBuffer()

		# modifications = {'block': {}, 'entity': {}}
		# # Iterate through all modifications and load them into a dictionary
		# for namespace in (namespace for namespace in listdir(f'{version_name}/modifications') if isdir(f'{version_name}/modifications/{namespace}')):
		# 	for group_name in (group_name for group_name in listdir(f'{version_name}/modifications/{namespace}') if isdir(f'{version_name}/modifications/{namespace}/{group_name}')):
		# 		# load the modifications for that namespace and group name
		# 		if '__include_blocks__.json' in listdir(f'{version_name}/modifications/{namespace}/{group_name}'):
		# 			if namespace not in modifications['block']:
		# 				modifications['block'][namespace] = {}
		# 			if group_name not in modifications['block'][namespace]:
		# 				modifications['block'][namespace][group_name] = {"remove": [], "add": {}}
		# 			json_object = load_file(f'{version_name}/modifications/{namespace}/{group_name}/__include_blocks__.json')
		# 			for key, val in json_object.items():
		# 				if key in modifications['block'][namespace][group_name]:
		# 					print(f'Key "{key}" specified for addition more than once')
		# 				try:
		# 					modifications['block'][namespace][group_name]['add'][key] = primitives.get_block('blockstate', val)
		# 					modifications['block'][namespace][group_name]["remove"].append(key)
		# 				except:
		# 					print(f'could not get primitive "{val}"')
		# 					continue
		#
		# 		if '__include_entities__.json' in listdir(f'{version_name}/modifications/{namespace}/{group_name}'):
		# 			if namespace not in modifications['entity']:
		# 				modifications['entity'][namespace] = {}
		# 			if group_name not in modifications['entity'][namespace]:
		# 				modifications['entity'][namespace][group_name] = {"remove": [], "add": {}}
		# 			json_object = load_file(f'{version_name}/modifications/{namespace}/{group_name}/__include_entities__.json')
		# 			for key, val in json_object.items():
		# 				if key in modifications['entity'][namespace][group_name]:
		# 					print(f'Key "{key}" specified for addition more than once')
		# 				try:
		# 					modifications['entity'][namespace][group_name]['add'][key] = primitives.get_entity(val)
		# 				except:
		# 					print(f'could not get primitive "{val}"')
		# 					continue

		# load the block list the server created
		block_palette: dict = load_file(f'{version_name}/block_palette.json')
		blocks = {}

		for blockstate in block_palette['blocks']:
			namespace, base_name = blockstate['name'].split(':', 1)
			if (namespace, base_name) not in blocks:
				blocks[(namespace, base_name)] = {
					"properties": {prop['name']: [to_snbt(prop['type'], prop['value'])] for prop in blockstate['states']},
					"defaults": {prop['name']: to_snbt(prop['type'], prop['value']) for prop in blockstate['states']},
					"nbt_properties": True
				}
			else:
				for prop in blockstate['states']:
					snbt_value = to_snbt(prop['type'], prop['value'])
					if snbt_value not in blocks[(namespace, base_name)]['properties'][prop['name']]:
						blocks[(namespace, base_name)]['properties'][prop['name']].append(snbt_value)

		for (namespace, base_name), spec in blocks.items():
			save_json(f'{version_name}/block/blockstate/specification/{namespace}/vanilla/{base_name}.json', spec, buffer=output)

		return output.save()
	else:
		raise Exception(f'Could not find {version_name}/generated/reports/blocks.json')