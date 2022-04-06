from libtad import AstronomyService
from libtad import TimeService
from libtad.datatypes.places import Coordinates, LocationId
from libtad.datatypes.time import TADDateTime
from libtad.datatypes.astro import AstronomyEventClass, AstronomyObjectType

coordinates = Coordinates(59.743, 10.204)
place = LocationId(coordinates)
date = TADDateTime(2020, 11, 26)
service = AstronomyService("sdV4VfLW1J", "urvp9Ka73g6q7BZ0Fd4U")
service2 = TimeService("sdV4VfLW1J", "urvp9Ka73g6q7BZ0Fd4U")
service2.include_list_of_time_changes = True
service.include_timezone_information = True
service2.types = AstronomyEventClass.Meridian | AstronomyEventClass.Phase


result = service2.current_time_for_place(place)
astro_info = service.get_astronomical_info(AstronomyObjectType.Moon, place, date)
print (astro_info)
print (result)
