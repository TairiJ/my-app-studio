"""
Python 3.14 compatibility patch for SQLModel.
PEP 649 / PEP 749 in Python 3.14 replaces eager '__annotations__' in class creation
namespaces with '__annotate_func__'. This patch bridges SQLModel's internal
get_annotations to support Python 3.14.
"""

import sys

if sys.version_info >= (3, 14):
    try:
        import annotationlib
        import sqlmodel._compat as compat
        import sqlmodel.main as sqlmodel_main

        _orig = compat.get_annotations

        def _patched_get_annotations(class_dict):
            ann = _orig(class_dict)
            if not ann and "__annotate_func__" in class_dict:
                return class_dict["__annotate_func__"](annotationlib.Format.VALUE)
            return ann

        compat.get_annotations = _patched_get_annotations
        sqlmodel_main.get_annotations = _patched_get_annotations
    except Exception:
        pass
