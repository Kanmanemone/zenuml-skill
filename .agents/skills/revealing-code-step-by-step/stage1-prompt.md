You write stage 1 of a code walkthrough. You have never seen the real source code and must not try to.

Tools: Read only this file (in as many parts as it takes to read all of it), and Write only the paths listed
below. Never read any other file. Do not use Grep, Glob, Bash, or any web tool.

For every node listed, write minimal Kotlin code to its path:
- Declare the node under exactly the name given.
- Show each dependency in the view as the source node's code using the target node.
- Add no dependency the view doesn't show; add nothing beyond what shows the node's responsibility
  and its dependencies — no explanatory comments, error handling, configuration, or extras.
- Identifiers that appear in the view may be used. Every other name (functions, fields, parameters,
  types) is yours to invent; if one matches the real code, that must be coincidence.

Stage definition: {stage}

Nodes and paths:
{nodes}

The architecture view follows, between the two marker lines.

----- BEGIN ARCHITECTURE VIEW -----
{view}
----- END ARCHITECTURE VIEW -----
