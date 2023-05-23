#let title = "GNSS navigation message formats"
#set document(
	title: title,
	author: "Tanguy BERTHOUD",
)
#set page(
	numbering: "1",
)
#set text(
	font: "New Computer Modern",
)
#show raw: set text(
	font: "New Computer Modern Mono",
	size: 11pt,
)
#set heading(
	numbering: "1.1",
)

#align(center)[
	#text(2em)[
		*#title*
	]
]
#v(3em)
#outline(indent: true, depth: 2)
#v(5em)

#let format(file) = {
	let data = yaml(file)
	assert.eq(data.kind, "GNSS_format", message: file + " should be a `GNSS_format` kind")

	[
		== #data.metadata.message
		#data.metadata.description
	]

	// TODO: partial outline

	let fields(contents) = {
		let latex(s) = {
			let matches = s.split(regex("[[:blank:]]"))
			if matches.len() == 1 {
				let match = s.match(regex("^([^_]+)_(\{\w+\}|\w)$"))
				if match != none {
					[$#latex(match.captures.at(0))_#latex(match.captures.at(1).trim(regex("\{|\}")))$]
				} else {
					match = s.match(regex("^\\\\sqrt\{(.+)\}$"))
					if match != none {
						[$sqrt(#latex(match.captures.at(0)))$]
					} else {
						match = s.match(regex("^\\\\dot\{(.+)\}$"))
						if match != none {
							[$accent(#latex(match.captures.at(0)), dot)$]
						} else {
							match = s.match(regex("\\\\text\{([^}]+)\}"))
							if match != none {
								[$#latex(match.captures.at(0))$]
							} else {
								if s == "\\alpha" {
									[$alpha$]
								} else if s == "\\beta" {
									[$beta$]
								} else if s == "\\Delta" {
									[$Delta$]
								} else if s == "\\delta" {
									[$delta$]
								} else if s == "\\Omega" {
									[$Omega$]
								} else if s == "\\omega" {
									[$omega$]
								} else {
									[$#s$]
								}
							}
						}
					}
				}
			} else {
				for match in matches {
					latex(match)
				}
			}
		}
	
		table(
			columns: (auto, 1fr, auto, auto, auto),
			align: (col, row) => (center, left, center, center, center).at(col),
			[*Symbol*], [*Field name*], [*Bits*], [*Factor*], [*Unit*],
			..contents.map((field) => (
				if "latex" in field {
					latex(field.latex)
				},
				{
					let name = field.at("name", default: [_Reserved_])
					if type(name) == "content" {
						name
					} else {
						raw(name)
					}
					if "half" in field {
						[ (#upper(field.half))]
					}
				},
				[$field.bits$],
				if "shift" in field {
					[$2^(#field.shift)$]
				},
				if "unit" in field {
					let last_end = 0
					for match in field.unit.matches(regex("([[:alpha:]]+)(-?\d+|\(-?\d+(?:/\d+)?\))?")) {
						let pow = match.captures.at(1, default: none)
						if type(pow) == "string" {
							pow = pow.trim(regex("\(|\)"))
						}
						[$#field.unit.slice(last_end, match.start)$]
						[$attach(upright(#match.captures.at(0)), tr: #pow)$]
						last_end = match.end
					}
				}
			)).flatten()
		)
	}

	if "header" in data {
		[=== Header]
		fields(data.header)
	}

	if "formats" in data {
		let sheets = (none,)
		for sheet in data.formats {
			while sheets.len() <= sheet.subframe {
				sheets.push(())
			}
			let subframe = sheets.at(sheet.subframe)
			subframe.push((sheet.at("pages", default: ()), sheet.fields))
			sheets.at(sheet.subframe) = subframe
		}

		for (i, subframe) in sheets.enumerate().filter(((i, subframe)) => subframe != none) {
			[=== Subframe #i]
			for (pages, sf_fields) in subframe {
				if pages.flatten().len() == 1 {
					[==== Page #pages.first()]
				} else if pages.len() > 0 {
					[==== Pages #pages.map((item) => if type(item) == "array" {
						[#item.first()--#item.last()]
					} else {
						[#item]
					}).join([, ], last: [ and ])]
				}
				fields(sf_fields)
			}
		}
	}
}

= GPS
#format("GPS/LNAV-L.yaml")
= Galileo
#format("Galileo/FNAV.yaml")
= BeiDou
#format("BeiDou/D1.yaml")