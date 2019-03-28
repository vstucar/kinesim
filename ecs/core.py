import stdevent

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

    __events = {}

    @staticmethod
    def subscribe( id, callback):
        if id not in EventBus.__events:
            EventBus.__register(id)
        EventBus.__events[id].append(callback)

    @staticmethod
    def unsubscribe(id, callback):
        if id in EventBus.__events:
            del EventBus.__events[callback]

    @staticmethod
    def publish(id, data):
        if id not in EventBus.__events:
            EventBus.__register(id)
        for callback in EventBus.__events[id]:
            callback(data)

    @staticmethod
    def __register(id):
        print('Event %d registred' % id)
        if id not in EventBus.__events:
            EventBus.__events[id] = []


class Engine(object):
    """
    Holds all objects and control everything
    """

    def __init__(self):
        print('Engine init')
        self.__entities = []
        self.__components = []

        EventBus.subscribe(stdevent.EVENT_COMPONENT_ADDED, self.__component_added)
        EventBus.subscribe(stdevent.EVENT_COMPONENT_REMOVED, self.__component_removed)
        EventBus.publish(stdevent.EVENT_SETUP, self)

    def __del__(self):
        EventBus.publish(stdevent.EVENT_TEARDOWN)

    def __component_added(self, component):
        print('component {} added to engine'.format(component))
        self.__components.append(component)

    def __component_removed(self, component):
        print('component {} removed from engine'.format(component))
        self.__components.remove(component)

    def update(self):
        EventBus.publish(stdevent.EVENT_UPDATE, self)

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


class BaseComponent(object):
    """
    Base class for components, allows access to it's parent entity
    """

    def __init__(self):
        self.__parent = None

    def added(self, parent):
        """
        Registers component in Entity
        :param parent: Entity component added to
        """
        if self.__parent is None:
            self.__parent = parent
        else:
            raise SystemError('Component already added to the entity')

    def removed(self):
        """
        Frees component from Entity
        :return:
        """
        if self.__parent is not None:
            self.__parent = None
        else:
            raise SystemError('Component not added to entity')

    @property
    def parent(self):
        return self.__parent


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
        """
        Adds component to the entity.
        Component can be added only once.
        Component can't belong to the multiple entities.
        :param component: Component to add
        """
        if component.parent is not None:
            raise RuntimeError('Component can belong only to one entity')

        if component.__class__ not in self.__components:
            self.__components[component.__class__] = [component]
            component.added(self)
            EventBus.publish(stdevent.EVENT_COMPONENT_ADDED, component)
        else:
            clist = self.__components[component.__class__]
            if component not in clist:
                component.parent = self
                clist.append(component)
                component.added(self)
                EventBus.publish(stdevent.EVENT_COMPONENT_ADDED, component)
            else:
                raise RuntimeError('Component already added')

    def remove_component(self, component):
        """
        Removes component from the entity
        :param component: Component to remove
        """
        for comp_class in self.__components:
            if component in self.__components[comp_class]:
                self.__components[comp_class].remove(component)
                component.removed()
                EventBus.publish(stdevent.EVENT_COMPONENT_REMOVED, component)
                return
        raise RuntimeError('Component not in entity')

    @property
    def components(self):
        """
        Gets map all entity's components.
        WARNING: This methods returns actual dictionary, DO NOT MODIFY MANUALLY
        :return:
        """
        return self.__components

    def get_components_by_class(self, component_class):
        """
        Gets all components of given class
        :param component_class: Required class of components
        :return: List of components with class @component_class or empty list
                 if there is no components with given class
        """
        return self.__components[component_class]

    def get_first_component_by_class(self, component_class):
        """
        Gets first component of given class
        :param component_class: Required class of components
        :return: First component with class @component_class or None
                 if there is no components with given class
        """
        return next(iter(self.get_components_by_class(component_class)), None)

    def has_components_of_class(self, component_class):
        """
        Checks is there are any components of given class in Entity
        :param component_class: Required class of components
        :return: True/False - has class or not.
        """
        return len(self.get_components_by_class(component_class)) > 0
