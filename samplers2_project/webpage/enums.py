from enum import Enum

class StepType(Enum):
	DATESTEP = "DateStep"
	TEXTSTEP = "TextStep"
	INFORMATIONSTEP = "InformationStep"
	PHOTOSTEP = "PhotoStep"
	LOCATIONSTEP = "LocationStep"
	SELECTONESTEP = "SelectOneStep"
	SELECTMULTIPLESTEP = "SelectMultipleStep"
	TIMESTEP = "TimeStep"
	ROUTESTEP = "RouteStep"
	SOUNDRECORDSTEP = "SoundRecordStep"


