# Markdown reference

This page demonstrates every markdown feature supported by WikiNest. Use it to verify rendering and as a copy-paste reference when writing documentation.

---

## Headings

```
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

---

## Paragraphs and line breaks

A paragraph is one or more lines of text separated by a blank line.

This is a second paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

To force a line break within a paragraph, end a line with two spaces or a backslash.
Line two follows immediately.

---

## Emphasis

```
*italic* or _italic_
**bold** or __bold__
***bold italic*** or ___bold italic___
~~strikethrough~~
```

*italic* · **bold** · ***bold italic*** · ~~strikethrough~~

---

## Blockquotes

```
> Single level quote.

> First level.
>> Second level nested.
>>> Third level nested.
```

> Single level quote.

> First level.
>> Second level nested.
>>> Third level nested.

Blockquotes can contain other markdown:

> **Note:** this is important.
> Use them for callouts, warnings, or citations.

---

## Lists

### Unordered

```
- Item one
- Item two
  - Nested item
  - Another nested item
    - Deeply nested
- Item three
```

- Item one
- Item two
  - Nested item
  - Another nested item
    - Deeply nested
- Item three

### Ordered

```
1. First item
2. Second item
   1. Nested ordered
   2. Another nested
3. Third item
```

1. First item
2. Second item
   1. Nested ordered
   2. Another nested
3. Third item

### Mixed

- Unordered item
  1. Ordered nested
  2. Another ordered nested
- Back to unordered

### Task list

```
- [x] Completed task
- [ ] Incomplete task
- [x] Another done
```

- [x] Completed task
- [ ] Incomplete task
- [x] Another done

---

## Code

### Inline code

Use `backticks` for inline code. Example: run `npm install` to install dependencies.

### Fenced code blocks

With language for syntax highlighting:

```js
// JavaScript
const greet = (name) => {
  return `Hello, ${name}!`;
};

console.log(greet('WikiNest'));
```

```python
# Python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("WikiNest"))
```

```bash
# Bash
for file in docs/**/*.md; do
  echo "Processing: $file"
done
```

```go
// Go
package main

import "fmt"

func main() {
    fmt.Println("Hello, WikiNest!")
}
```

```yaml
# YAML
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
```

```json
{
  "site_name": "WikiNest",
  "lang": "en",
  "edit_password_hash": ""
}
```

```sql
SELECT p.title, p.path, p.excerpt
FROM pages p
WHERE p.path LIKE 'docs/%'
ORDER BY p.title ASC;
```

Without a language:

```
Plain text block.
No syntax highlighting.
Useful for output or generic preformatted text.
```

---

## Horizontal rules

Three or more hyphens, asterisks, or underscores on a line:

```
---
***
___
```

---

## Links

### Inline links

```
[WikiNest on GitHub](https://github.com/KeeGooRoomiE/wikinest)
[Link with title](https://github.com/ "GitHub homepage")
```

[WikiNest on GitHub](https://github.com/KeeGooRoomiE/wikinest)

### Reference-style links

```
[GitHub][gh] is where the code lives.

[gh]: https://github.com
```

[GitHub][gh] is where the code lives.

[gh]: https://github.com

### Internal links

```
[Installation](setup/installation)
[Configuration](setup/configuration)
```

[Installation](setup/installation) · [Configuration](setup/configuration)

### Bare URLs

<https://github.com/KeeGooRoomiE/wikinest>

---

## Images

```
![Alt text](https://via.placeholder.com/400x200 "Optional title")
```

![WikiNest placeholder](https://via.placeholder.com/600x200/E6F1FB/185FA5?text=WikiNest "WikiNest banner")

### Image as a link

```
[![Alt text](image-url)](link-url)
```

[![GitHub](https://via.placeholder.com/120x40/1f2328/ffffff?text=GitHub)](https://github.com)

---

## Tables

```
| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Cell 1 | Cell 2 | Cell 3 |
| Cell 4 | Cell 5 | Cell 6 |
```

| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Cell 1 | Cell 2 | Cell 3 |
| Cell 4 | Cell 5 | Cell 6 |

### Alignment

```
| Left | Center | Right |
|:---|:---:|---:|
| aligned left | centered | aligned right |
| `code` | **bold** | *italic* |
```

| Left | Center | Right |
|:---|:---:|---:|
| aligned left | centered | aligned right |
| `code` | **bold** | *italic* |

### Wider table

| Name | Type | Default | Description |
|---|---|---|---|
| `site_name` | string | `WikiNest` | Displayed in header and tab |
| `lang` | string | `en` | Default UI language |
| `edit_password_hash` | string | `""` | SHA-256 hash of edit password |
| `owner` | string | `""` | GitHub owner |
| `repo` | string | `""` | Repository name |

---

## Footnotes

Some text with a footnote.[^1] Another sentence with a different note.[^note]

[^1]: This is the first footnote.
[^note]: Footnotes can have multi-line content.

---

## Definition lists

WikiNest
: A lightweight wiki hosted on GitHub Pages with no server required.

Markdown
: A lightweight markup language with plain-text formatting syntax.

---

## Abbreviations

*[HTML]: HyperText Markup Language
*[API]: Application Programming Interface

Using HTML and API in text — hover over them to see the expansion (if supported by the renderer).

---

## Escaping

Use a backslash to escape special characters:

```
\*not italic\*
\`not code\`
\# not a heading
\[not a link\]
```

\*not italic\* · \`not code\` · \# not a heading

---

## HTML in markdown

Raw HTML is supported inside markdown:

<details>
<summary>Click to expand</summary>

This content is hidden by default and revealed on click. You can put any markdown here.

- Item one
- Item two

</details>

<br>

<kbd>Ctrl</kbd> + <kbd>K</kbd> — keyboard shortcut notation using `<kbd>` tags.

<mark>Highlighted text</mark> using the `<mark>` tag.

---

## Nested markdown in blockquotes

> ## Heading inside blockquote
>
> A paragraph inside a blockquote with **bold** and *italic* text.
>
> - List item one
> - List item two
>
> ```js
> // Code block inside blockquote
> const x = 42;
> ```

---

## Long content example

This section demonstrates how longer prose renders inside WikiNest.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

---

## Summary

| Element | Syntax |
|---|---|
| Heading | `# H1` `## H2` `### H3` |
| Bold | `**text**` |
| Italic | `*text*` |
| Strikethrough | `~~text~~` |
| Inline code | `` `code` `` |
| Code block | ```` ```lang ```` |
| Link | `[text](url)` |
| Image | `![alt](url)` |
| Blockquote | `> text` |
| Unordered list | `- item` |
| Ordered list | `1. item` |
| Task list | `- [x] done` |
| Table | `\| col \| col \|` |
| Horizontal rule | `---` |
| Footnote | `[^1]` |
