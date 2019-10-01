from typing import List, Tuple


class FunctionList:
	def __init__(self, data):
		assert isinstance(data, list)
		self._is_primitive = True
		self.function_list: List[BaseTranslationFunction] = []
		for fun in data:
			if fun['function'] in function_map:
				self.function_list.append(function_map[fun['function']](fun))
			else:
				raise Exception(f'No function name given for {data}')

	def extend(self, other: 'FunctionList'):
		assert isinstance(other, FunctionList)
		assert self._is_primitive == other._is_primitive
		if self._is_primitive:
			return self.primitive_extend(other)
		else:
			return self.compiled_extend(other)

	def primitive_extend(self, other: 'FunctionList'):
		"""Used to merge two primitive files together.
		The formats do not need to be identical but close enough that the data can stack."""

		# reorganise functions into the form
		# [
		#  [function_name, custom_name],
		#  [function_name, custom_name],
		#  [function_name, custom_name]
		# ]
		self_functions = [[fun.function_name, fun.custom_name] for fun in self.function_list]
		other_functions = [[fun.function_name, fun.custom_name] for fun in other.function_list]

		for fun, (fun_name, custom_name) in zip(other.function_list, other_functions):
			try:
				index = self_functions.index([fun_name, custom_name])
				self.function_list[index] += fun

			except ValueError:
				self.function_list.append(fun)
				self_functions.append([fun_name, custom_name])

	def compiled_extend(self, other):
		"""Used to merge two completed translations together.
		The formats must match in such a way that the two base translations do not interfere."""
		assert [fun.function_name for fun in self.function_list] == [fun.function_name for fun in other.function_list], f'The functions do not match\n{self.to_object()}\n{other.to_object()}'

		for self_fun, other_fun in zip(self.function_list, other.function_list):
			self_fun += other_fun

	def commit(self, extra_feature_set: Tuple[str, ...]):
		"""Confirm that the function is complete and run the validation code."""
		self._is_primitive = False
		self._commit(extra_feature_set)

	def _commit(self, extra_feature_set):
		for fun in self.function_list:
			fun.commit(extra_feature_set)

	def to_object(self):
		if self._is_primitive:
			raise Exception('The commit function must be called before to_object is called to confirm the format is valid')
		return [fun.to_object for fun in self.function_list]


class BaseTranslationFunction:
	function_name = None

	def __init__(self, data):
		self._is_primitive = True
		if 'custom_name' in data:
			self.custom_name = data['custom_name']
			del data['custom_name']
		else:
			self.custom_name = None
		self._function = data

	def __getitem__(self, item):
		return self._function[item]

	def __setitem__(self, key, value):
		self._function[key] = value

	def get(self, item, default):
		return self._function.get(item, default)

	def extend(self, other):
		assert isinstance(other, BaseTranslationFunction)
		if self._is_primitive:
			return self._primitive_extend(other)
		else:
			return self._compiled_extend(other)

	def _primitive_extend(self, other):
		"""Used to merge two primitive files together.
		The formats do not need to be identical but close enough that the data can stack."""
		raise NotImplemented

	def _compiled_extend(self, other):
		"""Used to merge two completed translations together.
		The formats must match in such a way that the two base translations do not interfere."""
		raise NotImplemented

	def commit(self, extra_feature_set: Tuple[str, ...]):
		"""Confirm that the function is complete and run the validation code."""
		self._is_primitive = False
		assert isinstance(self._function, dict)
		self._commit(extra_feature_set)

	def _commit(self, extra_feature_set: Tuple[str, ...]):
		raise NotImplemented

	def to_object(self):
		raise NotImplemented


from PyMCTCompiler.translation_functions.carry_nbt import CarryNBT
from PyMCTCompiler.translation_functions.carry_properties import CarryProperties
from PyMCTCompiler.translation_functions.map_block_name import MapBlockName
from PyMCTCompiler.translation_functions.map_nbt import MapNBT
from PyMCTCompiler.translation_functions.map_properties import MapProperties
from PyMCTCompiler.translation_functions.multiblock import Multiblock
from PyMCTCompiler.translation_functions.new_block import NewBlock
from PyMCTCompiler.translation_functions.new_entity import NewEntity
from PyMCTCompiler.translation_functions.new_nbt import NewNBT
from PyMCTCompiler.translation_functions.new_properties import NewProperties
from PyMCTCompiler.translation_functions.walk_input_nbt import WalkInputNBT

function_map = {f.function_name: f for f in [CarryNBT, CarryProperties, MapBlockName, MapNBT, MapProperties, Multiblock, NewBlock, NewEntity, NewNBT, NewProperties, WalkInputNBT]}
