
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = 'hEMU\xa2\xc5\xa7P\xb2\xc3\xd6\xec_\x96\xf3\xd3'
    
_lr_action_items = {'$end':([4,7,8,10,11,12,13,15,],[0,-2,-32,-1,-8,-5,-7,-6,]),'COLON':([1,9,],[6,14,]),'NAME':([0,3,5,7,8,11,12,13,15,],[1,9,1,-2,13,-8,15,-7,-6,]),'TAB':([2,6,14,],[8,-3,-4,]),'PERIOD':([0,5,7,8,11,12,13,15,],[3,3,-2,-32,-8,-5,-7,-6,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'target':([0,5,],[5,10,]),'target_name':([0,5,],[2,2,]),'name_list':([8,],[12,]),'target_list':([0,],[4,]),'body_code':([2,],[7,]),'empty':([8,],[11,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> target_list","S'",1,None,None,None),
  ('target_list -> target target','target_list',2,'p_target_list1','../ipymake/makefileparser.py',216),
  ('target -> target_name body_code','target',2,'p_target1','../ipymake/makefileparser.py',223),
  ('target_name -> NAME COLON','target_name',2,'p_target_name1','../ipymake/makefileparser.py',227),
  ('target_name -> PERIOD NAME COLON','target_name',3,'p_target_name2','../ipymake/makefileparser.py',231),
  ('body_code -> TAB name_list','body_code',2,'p_body_code','../ipymake/makefileparser.py',241),
  ('name_list -> name_list NAME','name_list',2,'p_name_list1','../ipymake/makefileparser.py',249),
  ('name_list -> NAME','name_list',1,'p_name_list2','../ipymake/makefileparser.py',254),
  ('name_list -> empty','name_list',1,'p_name_list3','../ipymake/makefileparser.py',259),
  ('config_defn -> topdict_list','config_defn',1,'p_config_defn','../ipymake/makefileparser.py',271),
  ('topdict_list -> topdict_list topdict_defn','topdict_list',2,'p_topdict_list1','../ipymake/makefileparser.py',279),
  ('topdict_list -> topdict_defn','topdict_list',1,'p_topdict_list2','../ipymake/makefileparser.py',284),
  ('topdict_list -> empty','topdict_list',1,'p_topdict_list3','../ipymake/makefileparser.py',288),
  ('topdict_defn -> LEFT_ANGLE NAME RIGHT_ANGLE dict_elem_list','topdict_defn',4,'p_topdict_defn','../ipymake/makefileparser.py',295),
  ('dict_defn -> LEFT_BRACE dict_elem_list RIGHT_BRACE','dict_defn',3,'p_dict_defn','../ipymake/makefileparser.py',302),
  ('dict_elem_list -> dict_elem_list dict_member_defn','dict_elem_list',2,'p_dict_elem_list1','../ipymake/makefileparser.py',309),
  ('dict_elem_list -> dict_member_defn','dict_elem_list',1,'p_dict_elem_list2','../ipymake/makefileparser.py',314),
  ('dict_elem_list -> empty','dict_elem_list',1,'p_dict_elem_list3','../ipymake/makefileparser.py',318),
  ('dict_member_defn -> NAME EQUAL data_defn','dict_member_defn',3,'p_dict_member_defn','../ipymake/makefileparser.py',322),
  ('list_defn -> LEFT_SQUARE list_elem_list RIGHT_SQUARE','list_defn',3,'p_list_defn','../ipymake/makefileparser.py',330),
  ('list_elem_list -> list_elem_list COMMA data_defn','list_elem_list',3,'p_list_elem_list_1','../ipymake/makefileparser.py',334),
  ('list_elem_list -> list_elem_list data_defn','list_elem_list',2,'p_list_elem_list_4','../ipymake/makefileparser.py',341),
  ('list_elem_list -> data_defn','list_elem_list',1,'p_list_elem_list_2','../ipymake/makefileparser.py',348),
  ('list_elem_list -> empty','list_elem_list',1,'p_list_elem_list_3','../ipymake/makefileparser.py',355),
  ('tuple_defn -> NAME LEFT_PAREN dict_elem_list RIGHT_PAREN','tuple_defn',4,'p_tuple_defn','../ipymake/makefileparser.py',363),
  ('data_defn -> NAME','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',370),
  ('data_defn -> NUMBER','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',371),
  ('data_defn -> string','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',372),
  ('data_defn -> tuple_defn','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',373),
  ('data_defn -> list_defn','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',374),
  ('data_defn -> dict_defn','data_defn',1,'p_data_defn','../ipymake/makefileparser.py',375),
  ('string -> STRING_LITERAL','string',1,'p_string','../ipymake/makefileparser.py',379),
  ('empty -> <empty>','empty',0,'p_empty','../ipymake/makefileparser.py',383),
]