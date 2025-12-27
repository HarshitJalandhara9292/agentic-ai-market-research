import { LitElement, html, css } from 'lit';
import Chart from 'chart.js/auto';
import { marked } from 'marked';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';


class MarketingUI extends LitElement {
  static styles = css`
  :host {
    display: block;
    --primary: #4f46e5;
    --primary-light: #6366f1;
    --bg: #f5f7ff;
    --card-bg: #ffffff;
    --radius: 16px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: var(--bg);
    min-height: 100vh;
    padding: 2rem;
  }

  h1 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 1.2rem;
    background: linear-gradient(90deg, #4f46e5, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    animation: fadeInDown 0.6s ease var(--d, 0s);
  }

  @keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .container {
    max-width: 850px;
    margin: auto;
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    animation: fadeIn 0.6s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  label {
    font-weight: 600;
    margin-top: 1rem;
    font-size: 0.95rem;
    display: block;
  }

  input, textarea, select {
    width: 100%;
    padding: 14px;
    margin-top: 6px;
    border-radius: 12px;
    border: 1px solid #dce1f5;
    background: #f8faff;
    transition: 0.25s ease;
    font-size: 1rem;
  }

  input:focus, textarea:focus, select:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(79,70,229,0.2);
    outline: none;
  }

  button {
    margin-top: 1.2rem;
    width: 100%;
    padding: 14px;
    font-size: 1.1rem;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    background: linear-gradient(90deg, #4f46e5, #6366f1);
    color: white;
    transition: 0.3s ease;
    box-shadow: 0 6px 15px rgba(99,102,241,0.3);
  }

  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(99,102,241,0.4);
  }

  /* Loading Overlay */
  .loader-overlay {
    position: fixed;
    inset: 0;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(3px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .spinner {
    width: 58px;
    height: 58px;
    border: 6px solid #ddd;
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .result-box {
    margin-top: 1.5rem;
    background: #fafbff;
    padding: 1.2rem;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.07);
    animation: fadeIn 0.4s ease;
  }

  .result-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--primary);
  }

  .result-title span {
    font-size: 1.6rem;
  }

  .content-box {
    white-space: pre-wrap;
    line-height: 1.6;
    font-size: 1rem;
    color: #333;
  }

  canvas {
    margin-top: 2rem;
    width: 100% !important;
    max-height: 350px;
  }
  
  .emoji {
  -webkit-text-fill-color: initial !important;
  background: none !important;
  display: inline-block;
}

`;

  static properties = {
    productName: { type: String },
    productDescription: { type: String },
    targetAudience: { type: String },
    budget: { type: String },
    agentChoice: { type: String },
    result: { type: Object },
    loading: { type: Boolean },
    completing: { type: Boolean },
  };

  constructor() {
    super();
    this.productName = '';
    this.productDescription = '';
    this.targetAudience = '';
    this.budget = '';
    this.agentChoice = 'Head of Marketing';
    this.result = null;
    this.loading = false;
    this.completing = false;
    this.chart = null;
  }

  isIncomplete(content) {
    if (!content) return false;
    const lastSentence = content.trim().split(/\s+/).slice(-5).join(' ');
    const incompletePatterns = [
      /\b(the|this|that|these|those|and|but|because|as|of|for|to|with)$/i,
      /\.\.\.$/,
      /[a-zA-Z]+:$/
    ];
    return incompletePatterns.some(p => p.test(lastSentence));
  }

  async completeContent(partialText) {
    this.completing = true;
    try {
      const res = await fetch('http://127.0.0.1:8000/complete_content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: partialText }),
      });
      const data = await res.json();
      if (data.completed_text) {
        this.result.content += '\n' + data.completed_text;
      }
    } catch (err) {
      console.error('Completion failed:', err);
    } finally {
      this.completing = false;
    }
  }

  formatBackendText(raw) {
    if (raw === null || raw === undefined) return '';
    if (typeof raw === 'object') {
      if (raw.content) return String(raw.content);
      if (raw.summary) return String(raw.summary);
      if (raw.json_dict && raw.json_dict.content) return String(raw.json_dict.content);
      if (raw.results && raw.results.raw) return String(raw.results.raw);
      return JSON.stringify(raw, null, 2);
    }

    let text = String(raw);
    try {
      const trimmed = text.trim();
      if ((trimmed.startsWith('{') || trimmed.startsWith('['))) {
        const parsed = JSON.parse(trimmed);
        return this.formatBackendText(parsed);
      }
      if (trimmed.startsWith('```') && trimmed.includes('```')) {
        const inner = trimmed.replace(/(^```.*?\n)|(```$)/, '').trim();
        try {
          const parsed = JSON.parse(inner);
          return this.formatBackendText(parsed);
        } catch {
          text = inner;
        }
      }
    } catch {}

    text = text.replace(/\\n/g, '\n')
               .replace(/\\"/g, '"')
               .replace(/\\t/g, '    ')
               .replace(/\\r/g, '\r');

    try {
      const maybe = JSON.parse(text);
      return this.formatBackendText(maybe);
    } catch {}

    return text.trim();
  }

  async runAgent() {
    if (!this.productName || !this.productDescription || !this.targetAudience || !this.budget) {
      alert('Please fill in all fields before running the agent!');
      return;
    }

    this.loading = true;
    this.result = null;

    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/run_agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: this.productName,
          product_description: this.productDescription,
          target_audience: this.targetAudience,
          budget: this.budget,
          agent_choice: this.agentChoice
        }),
      });

      const data = await response.json().catch(async () => {
        const txt = await response.text();
        return { summary: txt };
      });

      console.log('Response:', data);

      const cleaned = this.formatBackendText(data.summary || data.result || data || JSON.stringify(data));

      this.result = data;
      this._cleanedResultText = cleaned;

      const ctx = this.renderRoot.querySelector('#chartArea');
      if (ctx) {
        if (this.agentChoice === 'Head of Marketing') {
          const chartData = data.chart_data && data.chart_data.length ? data.chart_data : [
            { category: 'Research', value: 20000 },
            { category: 'Advertising', value: 15000 },
            { category: 'Content', value: 10000 },
            { category: 'Social Media', value: 15000 }
          ];
          const labels = chartData.map(c => c.category);
          const values = chartData.map(c => c.value);
          this.chart = new Chart(ctx, {
            type: 'pie',
            data: { labels, datasets: [{ data: values, backgroundColor: ['#007bff', '#00bcd4', '#ffc107', '#28a745'] }] }
          });
        } else if (this.agentChoice === 'Blog Writer') {
          const content = (data.json_dict && data.json_dict.content) || data.content || this._cleanedResultText || '';
          const wordCount = content ? content.split(/\s+/).length : 0;
          const headingCount = (content.match(/^#/gm) || []).length;
          const paragraphCount = (content.match(/\n\s*\n/g) || []).length;
          this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: ['Words', 'Headings', 'Paragraphs'],
              datasets: [{ label: 'Blog Structure', data: [wordCount, headingCount, paragraphCount], backgroundColor: ['#007bff', '#00bcd4', '#ffc107'] }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
          });
        }
      }

    } catch (err) {
      this.result = { error: err.message };
      this._cleanedResultText = '❌ Error: ' + err.message;
    } finally {
      this.loading = false;
    }
  }

  render() {
    // Example: Market Trends Bar Chart
    if (this.result?.sections?.['Market Trends & Opportunities']) {
      const trends = this.result.sections['Market Trends & Opportunities'];
      const ctx = document.getElementById('marketTrendsChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: trends.map(t => t.trend),
          datasets: [{
            label: 'Importance (%)',
            data: trends.map(t => t.importance),
            backgroundColor: 'rgba(54, 162, 235, 0.6)'
          }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
      });
    }

    const res = this.result || {};
    return html`
      <div class="container">
      <h1>Marketing Crew AI Dashboard <span class="emoji">🚀</span></h1>

        <label>Product Name:</label>
        <input type="text" placeholder="Enter product name..." @input=${e => this.productName = e.target.value}>

        <label>Product Description:</label>
        <textarea placeholder="Describe your product or campaign goal..." @input=${e => this.productDescription = e.target.value}></textarea>

        <label>Target Audience:</label>
        <input type="text" placeholder="e.g. Tech startups, students, etc." @input=${e => this.targetAudience = e.target.value}>

        <label>Budget (in USD):</label>
        <input type="number" placeholder="e.g. 50000" @input=${e => this.budget = e.target.value}>

        <label>Select Agent:</label>
        <select @change=${e => this.agentChoice = e.target.value}>
          <option>Head of Marketing</option>
          <option>Blog Writer</option>
          <option>SEO Specialist</option>
          <option>Social Media Creator</option>
          <option>All Agents</option>
        </select>

        <button @click=${this.runAgent} ?disabled=${this.loading}>
          ${this.loading ? 'Running...' : 'Run Agent'}
        </button>

        ${this.loading ? html`<div class="loader"></div>` : html``}

        ${this.result ? html`
         <div class="content-box">
          <b>📰 Output:</b><br>
          ${res.content?.content
            ? unsafeHTML(marked(res.content.content))
            : res.content
              ? unsafeHTML(marked(res.content))
              : this._cleanedResultText
                ? unsafeHTML(marked(this._cleanedResultText))
                : JSON.stringify(res, null, 2)}
          </div>

            ${this.completing ? html`<div class="completing">✨ Completing content...</div>` : ''}
          </div>

          <canvas id="chartArea"></canvas>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('marketing-ui', MarketingUI);
