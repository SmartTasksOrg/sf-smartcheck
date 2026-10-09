// Flowise custom node for SmartCheck (IAIso governance).
// Copy this folder into Flowise's components/nodes/ (or load as a custom tool).
// It shells out to the shipped adapter.py, so sf-smartcheck must be importable
// (install SmartCheck from a clone: python -m pip install . ; it is not on PyPI yet)
// or PYTHONPATH set to the repo src/.
const path = require('path');
const { spawnSync } = require('child_process');

class SmartCheck_Node {
  constructor() {
    this.label = 'SmartCheck';
    this.name = 'smartcheck_check';
    this.version = 1.0;
    this.type = 'SmartCheck';
    this.category = 'SmartTasks / IAIso Governance';
    this.description = "Flag confident-but-unsourced AI output: unsourced numbers, contradictions, hedging, seeded errors.";
    this.baseClasses = [this.type, 'Tool'];
    this.inputs = [
      { label: 'Input (text)', name: 'input', type: 'string' },
      { label: 'Python', name: 'python', type: 'string', default: 'python3', optional: true },
    ];
  }

  async init(nodeData) {
    const input = (nodeData.inputs && nodeData.inputs.input) || '';
    const py = (nodeData.inputs && nodeData.inputs.python) || 'python3';
    const adapter = path.join(__dirname, '..', 'adapter.py');
    const res = spawnSync(py, [adapter, '--file', input], { encoding: 'utf8' });
    if (res.status !== 0) throw new Error(res.stderr || 'SmartCheck adapter failed');
    return JSON.parse(res.stdout);
  }
}

module.exports = { nodeClass: SmartCheck_Node };
