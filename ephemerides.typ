// LTeX: enabled=false

#import "@preview/bytefield:0.0.7": *
#import "@preview/mitex:0.2.5": mi

#set document(
  title: [Ephemerides --- GNSS navigations messages],
  author: ("Tanguy BERTHOUD"),
)
#show link: set text(fill: blue)
#show link: underline

#align(center, text(size: 2em, weight: "bold")[
  _Ephemerides_\
  GNSS navigation messages
])
#align(bottom, outline(depth: 2))
#pagebreak()

#set page(numbering: "1")


#let format(file, notes: (), heading_depth: 1) = {
  let fields(contents) = {
    let display_name(field) = {
      let name = field.at("name", default: none)
      if name == none {
        if "bits" in field and field.len() == 1 {
          [_Reserved_]
        } else {
          text(red)[_Unnamed_]
        }
      } else {
        raw(name)
      }
    }


    box(bytefield(
      bpr: 32,
      bitheader("bytes"),
      ..contents.enumerate().map(((i, field)) => bits(
        field.bits,
        fill: if (not "name" in field) and "bits" in field and field.len() == 1 { gray } else { white },
        if "latex" in field { mi(field.latex) } else { [\##(i + 1)] }
      ))
    ))
    table(
      columns: (auto, auto, 1fr, auto, auto, auto),
      align: (col, row) => (center, center, left, center, center, center).at(col),
      [*\#*], [*Symbol*], [*Field name*], [*Bits*], [*Factor*], [*Unit*],
      ..contents.enumerate().map(((i, field)) => (
        [#(i + 1)],
        if "latex" in field {
          mi(field.latex)
        },
        display_name(field),
        raw(
          if field.at("signed", default: false) { "i" } else { "u" }
          + str(field.bits)
        ),
        if "factor" in field {
          [$#field.factor$]
        } else if "shift" in field {
          [$2^#int(field.shift)$]
        },
        field.at("unit", default: "")
      ))
      .flatten()
    )
  }


  let data = yaml(file)
  assert.eq(data.kind, "GNSS_format", message: file + " should be a 'GNSS_format' kind")

  set heading(offset: heading_depth)

  heading(data.metadata.message)
  par(data.metadata.at("description", default: "").replace(regex("[[:space:]]+"), " "))

  for (i, (title, content)) in notes.enumerate() [
    == #title #label(data.metadata.message + "_note_" + str(i + 1))
    #content
  ]

  if "header" in data or "page_header" in data {
    [== Headers]
  }
  if "header" in data {
    [=== Subframe header #label(data.metadata.message + ".sh")]
    fields(data.header)
  }
  if "page_header" in data {
    [=== Page header #label(data.metadata.message + ".sph")]
    fields(data.page_header)
  }

  if "formats" in data {
    let subframes = ()
    for page in data.formats {
      while subframes.len() <= page.subframe {
        subframes.push(())
      }
      subframes.at(page.subframe).push(page)
    }
    for subframe in subframes.filter((subframe) => subframe.len() > 0) {
      let first = true
      for page in subframe {
        page.description = if "description" in page {
          text(
            style: if page.description == "Reserved" { "italic" } else { "normal" },
            page.description.replace(regex("[[:space:]]+"), " ")
          )
        } else {
          none
        }
        let pages = page.at("pages", default: ())
          .map((item) => (item,).flatten())
        let display_pages = pages
          .map((item) => if item.len() > 1 {
            [#item.first()--#item.last()]
          } else {
            [#item.first()]
          })
          .join(", ", last: " and ")

        if first {
          [== Subframe #page.subframe#if subframe.len() <= 1 and pages.len() == 0 and page.description != none [: #page.description] #label(data.metadata.message + ".s" + str(page.subframe))]
          first = false
        }
        if pages.len() > 0 {
          let label = label(data.metadata.message + ".s" + str(page.subframe) + "p" + str(pages.first().first()))
          if pages.len() == 1 {
            [=== Page #display_pages#if page.description != none [: #page.description] #label]
          } else {
            [=== Pages #display_pages#if page.description != none [: #page.description] #label]
          }
        }

        fields(page.fields)
      }
    }
  }
}


#let DATE_DISPLAY = "([weekday repr:long]) [month repr:long] [day padding:none], [year] [hour]:[minute]:[second]"

= GPS
#format("GPS/LNAV-L.yaml", notes: (
	([GPS Time], [
		#let start = datetime(year: 1980, month: 1, day: 6, hour: 0, minute: 0, second: 0)
		#let last_rollover = datetime(year: 2019, month: 4, day: 7, hour: 0, minute: 0, second: 0)
		#let next_rollover = datetime(year: 2038, month: 11, day: 21, hour: 0, minute: 0, second: 0)

		The GPS Time (GPST) is a continuous time scale (no _leap seconds_) starting on #start.display(DATE_DISPLAY).

		To compute the date from the LNAV-L message, two values are needed:
		- the *week number (WN)* found in the #link(<LNAV-L.s1>)[subframe 1]
		- the *time of week (TOW)* found in the #link(<LNAV-L.sh>)[subframe header]

		The time of week is a count defined as the number of subframes that have been sent since the last Sunday, 00:00:00.
		Each subframe spans *6 seconds*.\
		The time of week is related to the _Z-count_, a count defined as the number of X1 epochs that have occurred since the last Sunday, 00:00:00.
		An X1 epochs spans 1.5 seconds.
		Therefore, 1 TOW count equals 4 Z-counts.

		The week number is a count defined as the number of weeks that have occured since the zero time-point.
		But this value is broadcast on 10 bits, meaning that every 1024 weeks (about 19.7 years) the transmitted value _rolls over_ to 0 again.
		At the time of writing, the last rollover occurred on *#last_rollover.display(DATE_DISPLAY)*.
		The next one is planned on #next_rollover.display(DATE_DISPLAY).
	]),
	([`page_id` to documented page ID mapping], [
		While the ICD mentions page IDs ranging from 1 to 25, the effectively transmitted IDs (in the `page_id` fields) range from 1 to 63.

		#let map = (
			((1, 24), (1, 24)),
			((25, 28), (2, 5)),
			((29, 32), (7, 10)),
			(51, [25]),
			((52, 54), (13, 15)),
			((55, 56), (17, 18)),
			(57, [1, 6, 11, 16, 21]),
			((58, 59), (19, 20)),
			((60, 61), (22, 23)),
			(62, (12, 24)),
			(63, [25]),
		)
		#table(
			columns: 3 * (auto,),
			[*`page_id`*], [*Subframe*], [*ICD page ID*],
			..map.map(((page_id, icd)) => {
				let subframe = if page_id == (1, 24) or page_id == 51 { 5 } else { 4 }
				page_id = if type(page_id) == array and page_id.len() == 2 {
					[*#page_id.at(0)--#page_id.at(1)*]
				} else {
					[*#page_id*]
				}
				icd = if type(icd) == array and icd.len() == 2 {
					[#icd.at(0)--#icd.at(1)]
				} else {
					[#icd]
				}
				(page_id, [#subframe], icd)
			}).flatten()
		)

		#emoji.warning *The page IDs used in this document are `page_id` values*, not ICD page IDs!
	]),
))
#pagebreak()

= Galileo
#format("Galileo/FNAV.yaml")
#pagebreak()

= BeiDou
#format("BeiDou/D1.yaml", notes: (
	([BeiDou Time], [
		#let start = datetime(year: 2006, month: 1, day: 1, hour: 0, minute: 0, second: 0)
		#let next_rollover = datetime(year: 2163, month: 1, day: 2, hour: 0, minute: 0, second: 0)

		The BeiDou Time (BDT) is a continuous time scale (no _leap seconds_) starting on *#start.display(DATE_DISPLAY)*.

		To compute the date from the D1 message, two values are needed:
		- the *week number (WN)* found in the #link(<D1.s1>)[subframe 1]
		- the *time of week (SOW)* found in the #link(<D1.sh>)[subframe header]

		The time of week is defined as the number of seconds that have occurred since the last Sunday, 00:00:00.

		The week number is a count defined as the number of weeks that have occurred since the zero time-point.
		But this value is broadcast on 13 bits, meaning that every 8192 weeks (157.5 years) the transmitted value _rolls over_ to 0 again.
		At the time of writing, the next rollover should occur on #next_rollover.display(DATE_DISPLAY).
	]),
))
#pagebreak()

= GLONASS
#format("GLONASS/L1OC.yaml", notes: (
	([GLONASS Time], [
		#let start = datetime(year: 1996, month: 1, day: 1, hour: 0, minute: 0, second: 0)

		The GLONASS Time (GLONASST) is a time scale implementing _leap seconds_ (like UTC) starting on *#start.display(DATE_DISPLAY)*.
		$ "GLONASST" = "UTC"_"(SU)" + 0300 $

		To compute the date from the L1OC message, several values are needed:
		- the *four-year interval number* found in #link(<L1OC.s1p5>)[all subframes, page 5]
		- the *day number* found in #link(<L1OC.s1p4>)[all subframes, page 4]
		- the *hour*, *minute* and *second* found in #link(<L1OC.s1p1>)[all subframes, page 1]

		The four-year interval number is defined as the number of four-year intervals that have occurred since 1996.
		At the time of writing, this value is equal to #{ calc.floor((datetime.today().year() - 1996) / 4) }.

		The day number is defined as the number of days that have occurred since the beginning of the current four-year interval.
	]),
))
