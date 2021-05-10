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
        def __init__(self, source, dest, ass_type="default", multiplicity=('1','1'), para=[]):
            '''
            ass_type : "association", "generalization", "aggregation", "default"
            multiplicity: ('1','1'), ('1','*'), ('*', '*')
            para: a string list
            '''
            self.source = source
            self.dest = dest
            self.ass_type = ass_type
            self.multiplicity = multiplicity
            self.para = para

        def add_para(self, para):
            self.__para.append(para)

        def asdict(self):
            obj = {
                "source" : self.source,
                "dest" : self.dest,
                "type" : self.ass_type,
                "multiplicity" : self.multiplicity,
                "para" : tuple(ISDeDup.de_dup_list(self.para))

            }
            return obj


    class ISAttribute:
        def __init__(self, attr_name, attr_type="default"):
            '''
            att_type : all those primitive types, "object", "default"
            '''
            self.name = attr_name
            self.type = attr_type

        def asdict(self):
            obj = {
                "name" : self.name,
                "type" : self.type,
            }
            return obj


    class ISEntity:
        def __init__(self, entity_name, entity_type="default"):
            '''
            entity_type : entity, actor, default.
            '''
            self.name = entity_name
            self.type = [entity_type]
            self.attributes = []

        def add_entity_attribute(self, attr):
            self.attributes.append(attr)

        def add_entity_type(self, entity_type):
            self.type.append(entity_type)
            
        def asdict(self):
            obj = {
                "name" : self.name,
                "type" : ISDeDup.de_dup_list(self.type),
                "attributes" : ISDeDup.de_dup_list(self.attributes)
            }
            return obj


    class ISBehavior:
        def __init__(self, actor, action, target="", para=[]):
            self.actor = actor
            self.action = action
            self.target = target
            self.para = para


        def asdict(self):
            obj = {
                "actor" : self.actor,
                "action" : self.action,
                "target" : self.target,
                "para" : tuple(ISDeDup.de_dup_list(self.para))
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
    def add_relation(self, source, dest, ass_type="default", multiplicity=('1','1'), para=[]):
        # if actor not in self.__entity_dict:
        #     self.add_entity(actor)
        # if dest not in self.__entity_dict:
        #     self.add_entity(dest)
        relation = self.ISRelation(source, dest, ass_type, multiplicity, para)
        self.__relation_list.append(relation)

    def delete_relation(self, source="", dest=""):
        for relation in self.__relation_list:
            if source != "" and relation.source == source and dest == "":
                self.__relation_list.remove(relation)
            elif dest != "" and relation.dest ==  dest and source == "":
                self.__relation_list.remove(relation)
            elif source != "" and dest != "" and relation.source == source and relation.dest == target:
                self.__relation_list.remove(relation)


    def relation_asdict(self):
         return json.loads(json.dumps(ISDeDup.de_dup_list(self.__relation_list), cls=ISComplexEncoder))

    # Entity ops
    def add_entity(self, entity_name, entity_type="entity"):
        if entity_name not in self.__entity_dict:
            entity = self.ISEntity(entity_name, entity_type)
            self.__entity_dict[entity_name] = entity
        else:
            self.__entity_dict[entity_name].add_entity_type(entity_type)

    def delete_entity(self, entity_name):
        self.__entity_dict.pop(entity_name, None)

    def add_entity_attribute(self, entity_name, attr_name, attr_type="default"):
        if entity_name not in self.__entity_dict:
            self.add_entity(entity_name)
        attribute = self.ISAttribute(attr_name, attr_type)
        self.__entity_dict[entity_name].add_entity_attribute(attribute)

    def entity_asdict(self):
        return json.loads(json.dumps(self.__entity_dict, cls=ISComplexEncoder))

    # Behavior ops
    def add_behavior(self, actor, action, target=""):
        # if actor not in self.__entity_dict:
        #     self.add_entity(actor)
        # if target != "" and target not in self.__entity_dict:
        #     self.add_entity(target)
        behavior = self.ISBehavior(actor, action, target)
        self.__behavior_list.append(behavior)

    def delete_behavior(self, actor="", target=""):
        for behavior in self.__behavior_list:
            if actor != "" and behavior.actor == actor and target == "":
                self.__behavior_list.remove(behavior)
            elif target != "" and behavior.target ==  target and actor == "":
                self.__behavior_list.remove(behavior)
            elif actor != "" and target != "" and behavior.actor == actor and behavior.target == target:
                self.__behavior_list.remove(behavior)



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



