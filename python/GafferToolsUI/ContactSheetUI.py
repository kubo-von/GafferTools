import Gaffer
import GafferImage

Gaffer.Metadata.registerNode(

	GafferImage.ContactSheet,

	"description",
	"""
	Ensures deep samples are sorted and non-overlapping, and optionally
	discards samples that are completely transparent, or covered by other
	samples.
	""",

)