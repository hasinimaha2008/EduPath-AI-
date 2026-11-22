"use client";

import React, { useState } from "react";
import { Check, Copy, Code2 } from "lucide-react";

interface AssistantMarkdownProps {
  content: string;
  className?: string;
}

// Code Block with Header and Copy Button
function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code: ", err);
    }
  };

  // Basic syntax highlight regex replacement for common keywords
  const highlightSyntax = (raw: string, lang: string) => {
    const lines = raw.split("\n");
    return lines.map((line, lIdx) => {
      // Basic highlighting tokens
      let formatted = line;

      // Handle comments
      if (line.trim().startsWith("#") || line.trim().startsWith("//") || line.trim().startsWith("--")) {
        return (
          <div key={lIdx} className="text-[#71717A] italic leading-6">
            {line}
          </div>
        );
      }

      return (
        <div key={lIdx} className="leading-6">
          {renderCodeTokens(line, lang)}
        </div>
      );
    });
  };

  // Tokenize code lines into keywords, strings, and standard text
  const renderCodeTokens = (line: string, lang: string) => {
    // Keywords for programming & SQL
    const keywordRegex = /\b(def|class|return|import|from|as|if|elif|else|for|while|try|except|with|async|await|const|let|var|function|new|public|private|static|void|int|float|string|bool|SELECT|FROM|WHERE|INSERT|INTO|UPDATE|DELETE|JOIN|LEFT|RIGHT|INNER|GROUP|BY|ORDER|HAVING|LIMIT|TABLE|PRIMARY|KEY|CREATE|DROP|ALTER|VARCHAR|TIMESTAMP|DECIMAL)\b/g;
    const stringRegex = /(".*?"|'.*?'|`.*?`)/g;

    // Split on strings first to avoid highlighting keywords inside strings
    const parts = line.split(stringRegex);

    return parts.map((part, pIdx) => {
      if ((part.startsWith('"') && part.endsWith('"')) || (part.startsWith("'") && part.endsWith("'")) || (part.startsWith("`") && part.endsWith("`"))) {
        return (
          <span key={pIdx} className="text-[#34D399]">
            {part}
          </span>
        );
      }

      // Inside non-string part, highlight keywords
      const subParts = part.split(keywordRegex);
      return (
        <React.Fragment key={pIdx}>
          {subParts.map((sub, sIdx) => {
            if (keywordRegex.test(sub)) {
              return (
                <span key={sIdx} className="text-[#C084FC] font-semibold">
                  {sub}
                </span>
              );
            }
            return <span key={sIdx} className="text-[#E2E8F0]">{sub}</span>;
          })}
        </React.Fragment>
      );
    });
  };

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-[#3B2654] bg-[#0C0814] shadow-lg">
      <div className="flex items-center justify-between px-4 py-2 bg-[#171026] border-b border-[#2D1B42] text-xs">
        <div className="flex items-center gap-1.5 text-[#C084FC] font-mono font-semibold tracking-wider uppercase text-[11px]">
          <Code2 className="w-3.5 h-3.5" />
          <span>{language || "code"}</span>
        </div>
        <button
          onClick={handleCopy}
          type="button"
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#241738] hover:bg-[#321F4E] text-[#D8B4FE] border border-[#3E255C] transition-all"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3 text-[#A855F7]" />
              <span>Copy code</span>
            </>
          )}
        </button>
      </div>
      <div className="p-4 font-mono text-xs overflow-x-auto text-[#E2E8F0]">
        <code>{highlightSyntax(code, language.toLowerCase())}</code>
      </div>
    </div>
  );
}

// Inline Markdown Parser for bold, italic, inline code, and links
function renderInlineMarkdown(text: string): React.ReactNode {
  if (!text) return null;

  // Pattern covers:
  // 1. Inline code: `code`
  // 2. Bold: **bold** or __bold__
  // 3. Italic: *italic* or _italic_
  // 4. Strikethrough: ~~del~~
  // 5. Links: [label](url)
  // 6. Math variables: $O(n)$
  const tokenRegex = /(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|~~[^~]+~~|\[[^\]]+\]\([^)]+\)|\$[^\$]+\$|\*[^*]+\*|_[^_]+_)/g;

  const parts = text.split(tokenRegex);

  return parts.map((part, index) => {
    if (!part) return null;

    // Inline Code: `code`
    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 mx-0.5 rounded bg-[#241738] text-[#E9D5FF] border border-[#442866] font-mono text-[12px]"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    // Bold: **text** or __text__
    if ((part.startsWith("**") && part.endsWith("**") && part.length >= 4) || (part.startsWith("__") && part.endsWith("__") && part.length >= 4)) {
      return (
        <strong key={index} className="font-semibold text-white">
          {renderInlineMarkdown(part.slice(2, -2))}
        </strong>
      );
    }

    // Strikethrough: ~~text~~
    if (part.startsWith("~~") && part.endsWith("~~") && part.length >= 4) {
      return (
        <del key={index} className="line-through text-[#71717A]">
          {renderInlineMarkdown(part.slice(2, -2))}
        </del>
      );
    }

    // Math: $formula$
    if (part.startsWith("$") && part.endsWith("$") && part.length >= 2) {
      return (
        <span
          key={index}
          className="font-mono text-[#F472B6] px-1 py-0.5 bg-[#2B1432] rounded text-[12px] border border-[#522058]"
        >
          {part.slice(1, -1)}
        </span>
      );
    }

    // Link: [label](url)
    const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/);
    if (linkMatch) {
      return (
        <a
          key={index}
          href={linkMatch[2]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#C084FC] underline decoration-purple-400 hover:text-white transition-colors"
        >
          {linkMatch[1]}
        </a>
      );
    }

    // Italic: *text* or _text_
    if ((part.startsWith("*") && part.endsWith("*") && part.length >= 2) || (part.startsWith("_") && part.endsWith("_") && part.length >= 2)) {
      return (
        <em key={index} className="italic text-[#E9D5FF]">
          {renderInlineMarkdown(part.slice(1, -1))}
        </em>
      );
    }

    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

// Full Markdown Component
export function AssistantMarkdown({ content, className = "" }: AssistantMarkdownProps) {
  if (!content) return null;

  // Split into blocks: code blocks, blockquotes, lists, headers, tables, paragraphs
  const renderBlocks = () => {
    const blocks: React.ReactNode[] = [];
    const lines = content.split("\n");
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // 1. Fenced Code Block
      if (line.trim().startsWith("```")) {
        const langMatch = line.trim().match(/^```([a-zA-Z0-9_\-+#]*)/);
        const language = langMatch && langMatch[1] ? langMatch[1] : "code";
        const codeLines: string[] = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith("```")) {
          codeLines.push(lines[i]);
          i++;
        }
        i++; // skip closing ```
        blocks.push(
          <CodeBlock
            key={`code-${blocks.length}-${i}`}
            language={language}
            code={codeLines.join("\n")}
          />
        );
        continue;
      }

      // 1.5 Display Math Block ($$...$$ or \[...\])
      if (line.trim().startsWith("$$") || line.trim().startsWith("\\[")) {
        const mathLines: string[] = [];
        let singleLine = false;

        if (line.trim().startsWith("$$") && line.trim().endsWith("$$") && line.trim().length > 2) {
          mathLines.push(line.trim().slice(2, -2).trim());
          singleLine = true;
          i++;
        } else if (line.trim().startsWith("\\[") && line.trim().endsWith("\\]") && line.trim().length > 2) {
          mathLines.push(line.trim().slice(2, -2).trim());
          singleLine = true;
          i++;
        }

        if (!singleLine) {
          if (line.trim().startsWith("$$")) mathLines.push(line.trim().slice(2));
          else if (line.trim().startsWith("\\[")) mathLines.push(line.trim().slice(2));
          i++;
          while (i < lines.length && !lines[i].trim().endsWith("$$") && !lines[i].trim().endsWith("\\]")) {
            mathLines.push(lines[i]);
            i++;
          }
          if (i < lines.length) {
            const lastL = lines[i].trim().replace(/\$\$$|\\\]$/, "");
            if (lastL) mathLines.push(lastL);
            i++;
          }
        }

        blocks.push(
          <div key={`math-${blocks.length}`} className="my-3 py-3 px-4 rounded-xl bg-[#150B22] border border-[#3E225C] overflow-x-auto text-center shadow-inner">
            <span className="font-mono text-xs sm:text-sm text-[#F472B6] tracking-wide inline-block leading-relaxed">
              {mathLines.join("\n").trim()}
            </span>
          </div>
        );
        continue;
      }

      // 2. Markdown Table Detection (| col1 | col2 |)
      if (line.trim().startsWith("|") && line.trim().endsWith("|") && lines[i + 1]?.trim().startsWith("|")) {
        const tableLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) {
          tableLines.push(lines[i]);
          i++;
        }

        if (tableLines.length >= 2) {
          const headerRow = tableLines[0]
            .split("|")
            .slice(1, -1)
            .map((c) => c.trim());
          const dataRows = tableLines
            .slice(2)
            .map((row) =>
              row
                .split("|")
                .slice(1, -1)
                .map((c) => c.trim())
            );

          blocks.push(
            <div key={`table-${blocks.length}`} className="my-3 overflow-x-auto rounded-xl border border-[#3B2654]">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-[#1C122C] border-b border-[#3B2654] text-[#C084FC]">
                    {headerRow.map((h, hIdx) => (
                      <th key={hIdx} className="px-3 py-2 font-semibold">
                        {renderInlineMarkdown(h)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2B1B42] bg-[#100A1C]">
                  {dataRows.map((r, rIdx) => (
                    <tr key={rIdx} className="hover:bg-[#1C122C]/50 transition-colors">
                      {r.map((c, cIdx) => (
                        <td key={cIdx} className="px-3 py-2 text-[#D4D4D8]">
                          {renderInlineMarkdown(c)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 3. Blockquotes (> quote)
      if (line.trim().startsWith(">")) {
        const quoteLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith(">")) {
          quoteLines.push(lines[i].replace(/^>\s?/, ""));
          i++;
        }
        blocks.push(
          <blockquote
            key={`quote-${blocks.length}`}
            className="my-3 pl-4 py-2 border-l-4 border-[#8B5CF6] bg-[#1E142F]/70 rounded-r-lg text-xs italic text-[#D8B4FE]"
          >
            {renderInlineMarkdown(quoteLines.join(" "))}
          </blockquote>
        );
        continue;
      }

      // 4. Headings
      if (line.startsWith("# ")) {
        blocks.push(
          <h1 key={`h1-${blocks.length}`} className="text-xl font-bold text-white mt-4 mb-2 pb-1 border-b border-[#3B2654]">
            {renderInlineMarkdown(line.slice(2))}
          </h1>
        );
        i++;
        continue;
      }
      if (line.startsWith("## ")) {
        blocks.push(
          <h2 key={`h2-${blocks.length}`} className="text-lg font-bold text-white mt-3.5 mb-1.5 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#A855F7]" />
            {renderInlineMarkdown(line.slice(3))}
          </h2>
        );
        i++;
        continue;
      }
      if (line.startsWith("### ")) {
        blocks.push(
          <h3 key={`h3-${blocks.length}`} className="text-sm font-bold text-[#E9D5FF] mt-3 mb-1">
            {renderInlineMarkdown(line.slice(4))}
          </h3>
        );
        i++;
        continue;
      }
      if (line.startsWith("#### ")) {
        blocks.push(
          <h4 key={`h4-${blocks.length}`} className="text-xs font-semibold text-[#C084FC] mt-2 mb-1 uppercase tracking-wide">
            {renderInlineMarkdown(line.slice(5))}
          </h4>
        );
        i++;
        continue;
      }

      // 5. Horizontal Rules (--- or ***)
      if (line.trim() === "---" || line.trim() === "***") {
        blocks.push(<hr key={`hr-${blocks.length}`} className="my-3 border-[#3B2654]" />);
        i++;
        continue;
      }

      // 6. Lists (Unordered or Ordered)
      const isUnordered = /^(\s*)[-*+]\s+/.test(line);
      const isOrdered = /^(\s*)\d+\.\s+/.test(line);

      if (isUnordered || isOrdered) {
        const listItems: { indent: number; ordered: boolean; text: string; num?: string }[] = [];
        while (i < lines.length) {
          const cur = lines[i];
          const uMatch = cur.match(/^(\s*)[-*+]\s+(.*)$/);
          const oMatch = cur.match(/^(\s*)(\d+)\.\s+(.*)$/);

          if (uMatch) {
            listItems.push({
              indent: uMatch[1].length,
              ordered: false,
              text: uMatch[2],
            });
            i++;
          } else if (oMatch) {
            listItems.push({
              indent: oMatch[1].length,
              ordered: true,
              num: oMatch[2],
              text: oMatch[3],
            });
            i++;
          } else {
            break;
          }
        }

        blocks.push(
          <ul key={`list-${blocks.length}`} className="my-2 space-y-1.5 text-xs text-[#E4E4E7]">
            {listItems.map((item, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2"
                style={{ marginLeft: `${item.indent * 8}px` }}
              >
                {item.ordered ? (
                  <span className="font-mono text-[#C084FC] shrink-0 font-semibold text-[11px] mt-0.5">
                    {item.num}.
                  </span>
                ) : (
                  <span className="w-1.5 h-1.5 rounded-full bg-[#A855F7] shrink-0 mt-1.5" />
                )}
                <span className="leading-relaxed">{renderInlineMarkdown(item.text)}</span>
              </li>
            ))}
          </ul>
        );
        continue;
      }

      // 7. Regular Paragraphs
      if (line.trim().length > 0) {
        blocks.push(
          <p key={`p-${blocks.length}`} className="text-xs leading-relaxed text-[#E4E4E7] my-1.5">
            {renderInlineMarkdown(line)}
          </p>
        );
      }

      i++;
    }

    return blocks;
  };

  return <div className={`assistant-markdown space-y-1 ${className}`}>{renderBlocks()}</div>;
}
