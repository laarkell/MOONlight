$ pip3 install libtad

from libtad import AstronomyService
    from libtad.datatypes.places import Coordinates, LocationId
    from libtad.datatypes.time import TADDateTime
    from libtad.datatypes.astro import AstronomyEventClass, AstronomyObjectType
    
    coordinates = Coordinates(59.743, 10.204)
    place = LocationId(coordinates)
    date = TADDateTime(2020, 11, 26)
    service = AstronomyService("sdV4VfLW1J", "urvp9Ka73g6q7BZ0Fd4U")
    service.types = AstronomyEventClass.Meridian | AstronomyEventClass.Phase

astro_info = service.get_astronomical_info(AstronomyObjectType.Moon, place, date)
    
