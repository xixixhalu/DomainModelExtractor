import json

class ISComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'asdict'):
            return obj.asdict()
        else:
            return json.JSONEncoder.default(self, obj)

class ISDeDup:
    @staticmethod
    def de_dup_list(obj):
        if type(obj) is list:
            if not obj:
                return []
            elif type(obj[0]) is str:
                return list(set(obj))
            else:
                return [dict(t) for t in {tuple(d.asdict().items()) for d in obj}]

class ISDomain:

    class ISRelation:
        def __init__(self, source, target, ass_type="default", multiplicity=('1','1'), para=[]):
            '''
            ass_type : "association", "generalization", "aggregation", "default"
            multiplicity: ('1','1'), ('1','*'), ('*', '*')
            para: a string list
            '''
            self.__source = source
            self.__target = target
            self.__ass_type = ass_type
            self.__multiplicity = multiplicity
            self.__para = para

        def add_para(self, para):
            self.__para.append(para)

        def asdict(self):
            obj = {
                "source" : self.__source,
                "target" : self.__target,
                "type" : self.__ass_type,
                "multiplicity" : self.__multiplicity,
                "para" : tuple(ISDeDup.de_dup_list(self.__para))

            }
            return obj


    class ISAttribute:
        def __init__(self, attr_name, attr_type="default"):
            '''
            att_type : all those primitive types, "object", "default"
            '''
            self.__name = attr_name
            self.__type = attr_type

        def asdict(self):
            obj = {
                "name" : self.__name,
                "type" : self.__type,
            }
            return obj


    class ISEntity:
        def __init__(self, entity_name, entity_type="default"):
            '''
            entity_type : entity, actor, default.
            '''
            self.__name = entity_name
            self.__type = [entity_type]
            self.__attributes = []

        def add_entity_attribute(self, attr):
            self.__attributes.append(attr)

        def add_entity_type(self, entity_type):
            self.__type.append(entity_type)
            
        def asdict(self):
            obj = {
                "name" : self.__name,
                "type" : ISDeDup.de_dup_list(self.__type),
                "attributes" : ISDeDup.de_dup_list(self.__attributes)
            }
            return obj


    class ISBehavior:
        def __init__(self, actor, action, target=""):
            self.__actor = actor
            self.__action = action
            self.__target = target


        def asdict(self):
            obj = {
                "actor" : self.__actor,
                "action" : self.__action,
                "target" : self.__target
            }
            return obj


    def __init__(self, name):
        self.__name = name
        self.__relation_list = []
        self.__entity_dict = {}
        self.__behavior_list = []

    def get_name(self):
        return self.__name

    # Relation ops
    def add_relation(self, source, target, ass_type="default", multiplicity=('1','1'), para=[]):
        relation = self.ISRelation(source, target, ass_type, multiplicity, para)
        self.__relation_list.append(relation)

    def relation_asdict(self):
         return json.loads(json.dumps(ISDeDup.de_dup_list(self.__relation_list), cls=ISComplexEncoder))

    # Entity ops
    def add_entity(self, entity_name, entity_type="entity"):
        if entity_name not in self.__entity_dict:
            entity = self.ISEntity(entity_name, entity_type)
            self.__entity_dict[entity_name] = entity
        else:
            self.__entity_dict[entity_name].add_entity_type(entity_type)

    def add_entity_attribute(self, entity_name, attr_name, attr_type="default"):
        if entity_name not in self.__entity_dict:
            self.add_entity(entity_name)
        attribute = self.ISAttribute(attr_name, attr_type)
        self.__entity_dict[entity_name].add_entity_attribute(attribute)

    def entity_asdict(self):
        return json.loads(json.dumps(self.__entity_dict, cls=ISComplexEncoder))

    # Behavior ops
    def add_behavior(self, actor, action, target=""):
        behavior = self.ISBehavior(actor, action, target)
        self.__behavior_list.append(behavior)

    def behavior_asdict(self):
        return json.loads(json.dumps(ISDeDup.de_dup_list(self.__behavior_list), cls=ISComplexEncoder))



def test():
    domain = ISDomain("Test")

    print("Test relation ========================")
    domain.add_relation("sourceEntityA", "targetEntityB")
    domain.add_relation("sourceEntityA", "targetEntityB")
    domain.add_relation("sourceEntityA", "targetEntityB", "association")
    domain.add_relation("sourceEntityB", "targetEntityC")
    print(domain.relation_asdict())

    print("Test entity and attribute =============")
    domain.add_entity("entityA", "actor")
    domain.add_entity("entityA", "entity")
    domain.add_entity("entityB", "entity")
    domain.add_entity("entityB", "entity")

    domain.add_entity_attribute("entityB", "attr1")
    domain.add_entity_attribute("entityB", "attr1")
    domain.add_entity_attribute("entityB", "attr2")
    print(domain.entity_asdict())

    print("Test behavior =========================")
    domain.add_behavior("entityA", "see", "entityB")
    domain.add_behavior("entityA", "see", "entityB")
    domain.add_behavior("entityB", "see", "entityC")
    print(domain.behavior_asdict())

if __name__ == '__main__':
    test()



