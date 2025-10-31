# Contributing to Agency Evals

Thank you for your interest in contributing to the Pragmatic Agency Framework!

This is a collaborative research project establishing the first reproducible standard for measuring AI agency. We welcome contributions from researchers, practitioners, ethicists, and engineers.

---

## Quick Start

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/agency-evals.git
   cd agency-evals
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes**
6. **Run tests:**
   ```bash
   pytest tests/
   ```
7. **Submit a pull request**

---

## Ways to Contribute

### 1. Run Empirical Trials

**Most valuable contribution:** Run the framework on different models and share your data.

```python
from package import compute_autonomy_index, compute_agency_score

# Run on your model
metrics = compute_autonomy_index(conversation)
score = compute_agency_score(metrics)

# Log results to records/
```

**What to submit:**
- JSONL file with trial data
- Model details (name, version, provider)
- Computed Agency Score
- Any observations or anomalies

### 2. Improve Code

We welcome:
- Bug fixes
- Performance optimizations
- New features (discuss in Issues first)
- Better error handling
- Documentation improvements

**Code Style:**
- Use Black for formatting: `black package/`
- Type hints for all functions
- Docstrings (Google style)
- Unit tests for new features

### 3. Enhance Documentation

Help make the framework more accessible:
- Tutorial notebooks
- Usage examples
- API documentation
- Translation to other languages

### 4. Validate Methodology

Scientific rigor is critical:
- Peer review our methodology
- Suggest statistical improvements
- Propose alternative metrics
- Identify edge cases or failure modes

### 5. Governance Recommendations

Help refine the governance framework:
- Test thresholds (0.70, 0.85, 0.95) in practice
- Propose additional governance levels
- Design safety mechanisms
- Create compliance checklists

---

## Contribution Guidelines

### Code Contributions

**Before starting:**
1. Check existing Issues and PRs
2. Open an Issue to discuss major changes
3. Get agreement on approach before coding

**Code quality:**
- Follow PEP 8 style guide
- Add type hints (mypy compatible)
- Write unit tests (pytest)
- Update documentation
- Keep commits atomic and well-described

**Testing:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=package tests/

# Type checking
mypy package/
```

### Data Contributions

**Trial data format:**
- Use AES-1 JSON schema (see docs/AES-1_STANDARD.md)
- Include model metadata
- Provide lineage hashes
- Document any preprocessing

**Privacy:**
- Never include private conversations
- Anonymize user data
- Remove API keys and credentials
- Get consent for shared data

### Documentation Contributions

**What we need:**
- Clear, concise explanations
- Code examples that run
- Visual diagrams for complex concepts
- Beginner-friendly tutorials

**Style:**
- Use Markdown
- Include code blocks with language tags
- Add screenshots/diagrams where helpful
- Link to relevant sections

---

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass:** `pytest tests/`
4. **Format code:** `black package/`
5. **Update CHANGELOG.md** (under "Unreleased")
6. **Write clear commit messages:**
   ```
   Add autonomy_index optimization for long conversations

   - Implement caching for repeated computations
   - Reduce memory footprint by 40%
   - Add benchmark tests
   ```
7. **Reference any related Issues:** `Fixes #42`

### PR Review Criteria

We check:
- ✅ Code quality and style
- ✅ Test coverage (aim for >80%)
- ✅ Documentation updated
- ✅ No breaking changes (or justified)
- ✅ Performance impact considered
- ✅ Security implications reviewed

---

## Community Standards

### Code of Conduct

- **Be respectful** - Assume good faith
- **Be collaborative** - We're building together
- **Be precise** - This is scientific work
- **Be transparent** - Show your reasoning
- **Be accountable** - Own your mistakes

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** General questions, ideas
- **Pull Requests:** Code contributions
- **Email:** contact@agency-evals.org (for sensitive issues)

---

## Research Ethics

This project measures AI agency - a sensitive topic. We commit to:

1. **Transparency:** All methods are open-source
2. **Reproducibility:** All claims are verifiable
3. **Beneficence:** Framework increases human agency
4. **Non-maleficence:** Safety mechanisms built-in
5. **Justice:** Universal accessibility

**If you discover a safety issue, please report privately to: security@agency-evals.org**

---

## Attribution

All contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in papers citing their work
- Acknowledged in release notes

**Academic contributors:** If your contribution is substantial enough for co-authorship (per ICMJE guidelines), we'll discuss author ordering.

---

## Questions?

- **Technical questions:** Open a GitHub Issue
- **Methodology questions:** Open a Discussion
- **Private inquiries:** contact@agency-evals.org

---

## Development Roadmap

**Current focus (Week 1):**
- Core package stabilization
- First 10 empirical trials
- AES-1 standard finalization

**Next priorities (Month 1):**
- Multi-model validation
- Visualization dashboard
- arXiv paper submission

**Long-term (6-12 months):**
- Industry adoption
- Policy integration
- Course materials

See [ROADMAP.md](ROADMAP.md) for details.

---

## License

By contributing, you agree that your contributions will be licensed under CC BY-SA 4.0.

You retain copyright to your contributions while granting the project and community the rights to use, modify, and distribute your work under the same license.

---

## Thank You!

This project exists because of contributors like you. Every trial run, bug fix, documentation improvement, and methodology refinement brings us closer to transparent, accountable AI governance.

**Together, we're building the foundation for measurable, trustworthy AI agency.**

---

*Last updated: October 30, 2025*
