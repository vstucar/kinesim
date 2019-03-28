#!/usr/bin/python
import os

# Events ID
EVENT_COMPONENT_ADDED = 1
EVENT_COMPONENT_REMOVED = 2
EVENT_ENTITY_ADDED = 3
EVENT_ENTITY_REMOVED = 4


class EventBus(object):
    """
    Provides passing messaging using publisher-subscriber
    model. Publisher can publish data with some message-id,
    Subscriber can register callback for new data with
    corresponding id.
    Note:
        - register id before pub/sub
        - subscriber is synchronous and all subscribers for
          corresponding id called immediately after publish
          called
    """

    __instance = None

    def __init__(self):
        print('EventBus init')
        self.__events = {}

    def register(self, id):
        print('Event %d registred' % id)
        if id not in self.__events:
            self.__events[id] = []

    def subscribe(self, id, callback):
        if id not in self.__events:
            raise RuntimeError('Event id is not registred')
        self.__events[id].append(callback)

    def unsubscribe(self, id, callback):
        if id in self.__events:
            self.__events.remove(callback)

    def publish(self, id, data):
        if id not in self.__events:
            raise RuntimeError('Event id is not registred')
        for callback in self.__events[id]:
            callback(data)

    @staticmethod
    def instance():
        if EventBus.__instance is None:
            EventBus.__instance = EventBus()
        return EventBus.__instance


class Engine(object):
    """
    Holds all objects and control everything
    """

    __instance = None

    def __init__(self):
        print('Engine init')
        self.__systems = []
        self.__entities = []
        self.__components = []

        EventBus.instance().register(EVENT_COMPONENT_ADDED)
        EventBus.instance().register(EVENT_COMPONENT_REMOVED)
        EventBus.instance().register(EVENT_ENTITY_ADDED)
        EventBus.instance().register(EVENT_ENTITY_REMOVED)

        EventBus.instance().subscribe(EVENT_COMPONENT_ADDED, self.__component_added)
        EventBus.instance().subscribe(EVENT_COMPONENT_REMOVED, self.__component_removed)

    def __component_added(self, component):
        print('__component_added')
        self.__components.append(component)

    def __component_removed(self, component):
        print('__component_removed')
        self.__components.remove(component)

    def update(self):
        for system in self.__systems:
            system.update()

    def add_system(self, system):
        if system not in self.__systems:
            self.__systems.append(system)
            system.setup()
        else:
            raise RuntimeError('System already added to the Engine')

    def remove_system(self, system):
        if system in self.__systems:
            self.__systems.remove(system)
            system.teardown()
        else:
            raise RuntimeError('System not in Engine')

    def add_entity(self, entity):
        if entity not in self.__entities:
            self.__entities.append(entity)
        else:
            raise RuntimeError('Entity already added to the Engine')

    def remove_entity(self, entity):
        if entity in self.__entities:
            self.__entities.remove(entity)
        else:
            raise RuntimeError('Entity not in the Engine')

    def get_entities_with_components(self, components_list):
        return [entity for entity in self.__entities if
                all((entity.has_component_class(comp) for comp in components_list))]

    def get_components_by_class(self, component_class):
        return [comp for comp in self.__components if isinstance(comp, component_class)]

    @staticmethod
    def instance():
        if Engine.__instance is None:
            Engine.__instance = Engine()
        return Engine.__instance


class BaseComponent(object):
    """
    Base class for components, allows access to it's parent entity
    """

    def __init__(self):
        self.__parent = None

    def added(self, parent):
        if self.__parent is None:
            self.__parent = parent
        else:
            raise SystemError('Component already added to the entity')

    def removed(self):
        if self.__parent is not None:
            self.__parent = None
        else:
            raise SystemError('Component not added to entity')


    @property
    def parent(self):
        return self.__parent


class EngineChild(object):
    """
    Base class for something belows to Engine
    """

    def __init__(self):
        self.__engine = None

    @property
    def engine(self):
        return self.__engine

    @engine.setter
    def engine(self, engine):
        if self.__engine is None:
            self.__engine = engine
        else:
            raise RuntimeError('Engine already set')


class Entity(object):
    """
    Entity is a container of the components.
    This class shouldn't be inherited
    """

    def __init__(self, name):
        self.__name = name
        self.__components = {}

    @property
    def name(self):
        return self.__name

    def add_component(self, component):
        if component.parent is not None:
            raise RuntimeError('Component can belong only to one entity')

        if component.__class__ not in self.__components:
            self.__components[component.__class__] = [component]
            component.added(self)
            EventBus.instance().publish(EVENT_COMPONENT_ADDED, component)
        else:
            clist = self.__components[component.__class__]
            if component not in clist:
                component.parent = self
                clist.append(component)
                component.added(self)
                EventBus.instance().publish(EVENT_COMPONENT_ADDED, component)
            else:
                raise RuntimeError('Component already added')

    def remove_component(self, component):
        for comp_class in self.__components:
            if component in self.__components[comp_class]:
                self.__components[comp_class].remove(component)
                component.removed()
                EventBus.instance().publish(EVENT_COMPONENT_REMOVED, component)
                return
        raise RuntimeError('Component not in entity')

    def get_components_by_class(self, component_class):
        return self.__components[component_class]

    def has_component_class(self, component_class):
        return len(self.get_components_by_class(component_class)) > 0


class BaseSystem(object):
    """
    Systems performs actions
    """

    def __init__(self):
        self.__inited = False
        self.__downed = False

    def setup(self):
        if self.__inited:
            raise RuntimeError('System already initialised')
        self.__inited = True

    def teardown(self):
        if not self.__downed:
            raise RuntimeError('System already deinitialised')
        self.__downed = True

    def update(self):
        pass


class UpdateSystem(BaseSystem):
    """
    System with update() method called every
    tick
    """
    def __unicode__(self, world):
        super(self.__class__, self).__init__(world)

    def update(self):
        pass

###################################################


class PositionComponent(BaseComponent):
    def __init__(self):
        super(PositionComponent, self).__init__()
        self.x = 0
        self.y = 0


class RenderSystem(UpdateSystem):
    def __init__(self):
        super(RenderSystem, self).__init__()

    def update(self):
        print('RenserSystem.update')
        positions = Engine.instance().get_components_by_class(PositionComponent)
        for pos_component in positions:
            print(pos_component.x, pos_component.y)


if __name__ == '__main__':
    Engine.instance()

    render = RenderSystem()
    Engine.instance().add_system(render)

    entity = Entity('ent1')
    entity.add_component(PositionComponent())
    Engine.instance().add_entity(entity)

    Engine.instance().update()