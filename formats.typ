#let title = "GNSS navigation message formats"
#set document(
	title: title,
	author: "Tanguy BERTHOUD",
)
#set text(
	font: "New Computer Modern",
)
#show raw: set text(
	font: "New Computer Modern Mono",
	size: 11pt,
)
#set heading(
	numbering: "I.1.1",
)

#align(center + horizon)[
	#text(4em)[
		*#title*
	]
]
#align(bottom)[
	#outline(indent: true, depth: 2)
]
#pagebreak()

#set page(
	numbering: "1",
)
#set par(
	justify: true,
)

#let format(file) = {
	let data = yaml(file)
	assert.eq(data.kind, "GNSS_format", message: file + " should be a `GNSS_format` kind")

	[
		== #data.metadata.message
		#data.metadata.description.replace(regex("[[:space:]]+"), " ")
	]

	locate(loc => {
		let q = query(heading.where(level: 2).or(heading.where(level: 1)).after(loc), loc)
		let end_q = query(selector(heading).after(loc), loc)
		if q.len() > 0 or end_q.len() > 0 {
			let target = selector(heading).after(loc)
			if q.len() > 0 {
				target = target.before(q.first().location(), inclusive: false)
			}
			v(1em)
			outline(
				title: none,
				indent: true,
				target: target,
			)
			v(1em)
		}
	})

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
					let name = field.at("name", default: none)
					if name == none {
						if "bits" in field and field.len() == 1 {
							text(style: "italic", "Reserved")
						} else {
							text(red)[_Unnamed_]
						}
					} else {
						raw(name)
					}
					if "half" in field {
						[ (#upper(field.half))]
					}
					if "value" in field {
						let dec = field.value
						let bin = if dec == 0 { "0" } else { "" }
						while dec > 0 {
							let rem = calc.rem(dec, 2)
							dec -= rem
							dec /= 2
							bin = str(rem) + bin
						}
						h(1fr)
						[$=$ #raw(bin)]
					}
				},
				[#if field.at("signed", default: false) { "i" } else { "u" }#field.bits],
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
						[$#field.unit.slice(last_end, match.start).trim()$]
						[$attach(upright(#match.captures.at(0)), tr: #pow)$]
						last_end = match.end
					}
				}
			)).flatten()
		)
	}

	if "header" in data or "page_header" in data {
		[=== Headers]
	}
	if "header" in data {
		[==== Subframe header]
		fields(data.header)
	}
	if "page_header" in data {
		[==== Page header]
		fields(data.page_header)
	}

	if "formats" in data {
		let sheets = (none,)
		for sheet in data.formats {
			while sheets.len() <= sheet.subframe {
				sheets.push(())
			}
			let subframe = sheets.at(sheet.subframe)
			subframe.push((
				sheet.at("pages", default: ()),
				sheet.at("description", default: ""),
				sheet.fields,
			))
			sheets.at(sheet.subframe) = subframe
		}

		for (i, subframe) in sheets.enumerate().filter(((i, subframe)) => subframe != none) {
			let first = true
			for (pages, description, sf_fields) in subframe {
				description = if description.len() > 0 {
					text(
						style: if description == "Reserved" { "italic" } else { "normal" },
						description.replace(regex("[[:space:]]+"), " ")
					)
				}
				if first {
					[=== Subframe #i#if subframe.len() <= 1 and description != none { [: #description] }]
					first = false
				}
				if pages.flatten().len() == 1 {
					[==== Page #pages.first()#if description != none { [: #description] }]
				} else if pages.len() > 0 {
					[==== Pages #pages.map((item) => if type(item) == "array" {
						[#item.first()--#item.last()]
					} else {
						[#item]
					}).join(", ", last: " and ")#if description != none { [: #description] }]
				}
				
				fields(sf_fields)
			}
		}
	}
}

= GPS
#format("GPS/LNAV-L.yaml")
#pagebreak()
= Galileo
#format("Galileo/FNAV.yaml")
#pagebreak()
= BeiDou
#format("BeiDou/D1.yaml")