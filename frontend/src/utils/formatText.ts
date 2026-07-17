export type ContentBlock =
  | { type: 'heading'; text: string }
  | { type: 'paragraph'; text: string }
  | { type: 'list'; items: string[] }

function cleanListMarker(line: string) {
  return line.replace(/^(\d+[.)、]|[-*])\s*/, '').trim()
}

function isListItem(line: string) {
  return /^(\d+[.)、]|[-*])\s+/.test(line)
}

function headingText(line: string) {
  const match = line.match(/^#{1,4}\s+(.+)$/)
  return match?.[1]?.trim() ?? null
}

export function parseContentBlocks(content: string): ContentBlock[] {
  const blocks: ContentBlock[] = []
  const paragraphLines: string[] = []
  let listItems: string[] = []

  function flushParagraph() {
    const text = paragraphLines.join('\n').trim()
    if (text) {
      blocks.push({ type: 'paragraph', text })
    }
    paragraphLines.length = 0
  }

  function flushList() {
    if (listItems.length) {
      blocks.push({ type: 'list', items: listItems })
      listItems = []
    }
  }

  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim()
    if (!line) {
      flushParagraph()
      flushList()
      continue
    }

    const heading = headingText(line)
    if (heading) {
      flushParagraph()
      flushList()
      blocks.push({ type: 'heading', text: heading })
      continue
    }

    if (isListItem(line)) {
      flushParagraph()
      listItems.push(cleanListMarker(line))
      continue
    }

    flushList()
    paragraphLines.push(line)
  }

  flushParagraph()
  flushList()
  return blocks
}
