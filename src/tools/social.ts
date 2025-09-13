/**
 * Main social tools implementing the CLAUDE.md specification
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';
import pino from 'pino';
import { v4 as uuidv4 } from 'uuid';
import {
  FetchContextsInputSchema,
  SuggestOpenersInputSchema,
  FetchContextsResponse,
  SuggestOpenersResponse,
  CandidateProfile
} from '../models/index.js';
import { ApifyAdapter } from '../adapters/index.js';
import { ThemeInferenceEngine } from '../utils/index.js';
import { XTools } from './x-tools.js';
import { LinkedInTools } from './linkedin-tools.js';

const logger = pino({ name: 'social-tools' });

export class SocialTools {
  private apify: ApifyAdapter;
  private xTools: XTools;
  private linkedinTools: LinkedInTools;
  private resourceStorage = new Map<string, string>(); // Simple in-memory storage

  constructor() {
    this.apify = new ApifyAdapter();
    this.xTools = new XTools();
    this.linkedinTools = new LinkedInTools();
  }

  /**
   * Define the social.fetch_contexts MCP tool (NEW)
   */
  getFetchContextsToolDefinition(): Tool {
    return {
      name: 'social.fetch_contexts',
      description: 'Build two profile contexts in parallel: LinkedIn and Apollo (placeholder)',
      inputSchema: {
        type: 'object',
        properties: {
          first_name: { type: 'string' },
          last_name: { type: 'string' },
          linkedin_url: { type: 'string' },
          organization_name: { type: 'string' },
          domain: { type: 'string' },
          apollo_limit: {
            type: 'number',
            minimum: 1,
            maximum: 3,
            default: 1
          },
          include_recent_posts_summary: {
            type: 'boolean',
            default: true
          }
        },
        required: ['first_name', 'last_name']
      }
    };
  }

  /**
   * Execute social.fetch_contexts tool
   */
  async executeFetchContexts(args: unknown): Promise<string> {
    try {
      const input = FetchContextsInputSchema.parse(args);
      const {
        first_name,
        last_name,
        linkedin_url,
        organization_name,
        domain,
        apollo_limit = 1,
        include_recent_posts_summary = true
      } = input;

      logger.info(`Fetching contexts for ${first_name} ${last_name}`);

      const contextId = uuidv4();
      const warnings: string[] = [];

      // Run in parallel: LinkedIn and Apollo (Apollo is placeholder)
      const [linkedinContext, apolloContext] = await Promise.allSettled([
        this.fetchLinkedInContext(linkedin_url, include_recent_posts_summary),
        this.fetchApolloContext(first_name, last_name, organization_name, domain, apollo_limit)
      ]);

      // Process LinkedIn context
      let linkedinContextContent = '';
      if (linkedinContext.status === 'fulfilled') {
        linkedinContextContent = linkedinContext.value;
      } else {
        warnings.push(`LinkedIn context failed: ${linkedinContext.reason}`);
        linkedinContextContent = `LinkedIn context unavailable: ${linkedinContext.reason}`;
      }

      // Process Apollo context (placeholder)
      let apolloContextContent = '';
      let apolloCandidates: CandidateProfile[] = [];
      if (apolloContext.status === 'fulfilled') {
        const result = apolloContext.value;
        apolloContextContent = result.context;
        apolloCandidates = result.candidates;
      } else {
        warnings.push(`Apollo context failed: ${apolloContext.reason}`);
        apolloContextContent = `Apollo integration coming soon. This is a placeholder context for ${first_name} ${last_name}`;
      }

      // Create combined context
      const combinedContext = this.createCombinedContext(
        linkedinContextContent,
        apolloContextContent,
        first_name,
        last_name
      );

      // Store contexts as resources
      const linkedinResourceUri = `resource://contexts/linkedin/${contextId}.md`;
      const apolloResourceUri = `resource://contexts/apollo/${contextId}.md`;
      const combinedResourceUri = `resource://contexts/combined/${contextId}.md`;

      this.resourceStorage.set(linkedinResourceUri, linkedinContextContent);
      this.resourceStorage.set(apolloResourceUri, apolloContextContent);
      this.resourceStorage.set(combinedResourceUri, combinedContext);

      const response: FetchContextsResponse = {
        linkedin_context: linkedinResourceUri,
        apollo_context: apolloResourceUri,
        combined_context: combinedResourceUri,
        apollo_candidates: apolloCandidates,
        warnings
      };

      logger.info(`Successfully created contexts for ${first_name} ${last_name}`);
      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Error in fetch_contexts:', error);
      return JSON.stringify({
        error: error instanceof Error ? error.name : 'UNKNOWN_ERROR',
        message: error instanceof Error ? error.message : 'An unexpected error occurred',
        timestamp: new Date().toISOString()
      }, null, 2);
    }
  }

  /**
   * Define the social.suggest_openers MCP tool
   */
  getSuggestOpenersToolDefinition(): Tool {
    return {
      name: 'social.suggest_openers',
      description: 'Generate 3 grounded conversation openers from LinkedIn and Apollo contexts',
      inputSchema: {
        type: 'object',
        properties: {
          linkedin_context_resource: { type: 'string' },
          apollo_context_resource: { type: 'string' },
          posts_combined_summary: { type: 'string' },
          tone_options: {
            type: 'array',
            items: { type: 'string' },
            default: ['casual', 'professional', 'playful']
          }
        },
        required: ['linkedin_context_resource', 'apollo_context_resource']
      }
    };
  }

  /**
   * Execute social.suggest_openers tool
   */
  async executeSuggestOpeners(args: unknown): Promise<string> {
    try {
      const input = SuggestOpenersInputSchema.parse(args);
      const {
        linkedin_context_resource,
        apollo_context_resource,
        posts_combined_summary,
        tone_options = ['casual', 'professional', 'playful']
      } = input;

      // Retrieve contexts from storage
      const linkedinContext = this.resourceStorage.get(linkedin_context_resource) || '';
      const apolloContext = this.resourceStorage.get(apollo_context_resource) || '';

      if (!linkedinContext && !apolloContext) {
        throw new Error('INSUFFICIENT_DATA: No context data available');
      }

      const openers = await this.generateOpeners(
        linkedinContext,
        apolloContext,
        posts_combined_summary,
        tone_options
      );

      const response: SuggestOpenersResponse = {
        openers,
        warnings: []
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Error in suggest_openers:', error);
      return JSON.stringify({
        error: error instanceof Error ? error.name : 'UNKNOWN_ERROR',
        message: error instanceof Error ? error.message : 'An unexpected error occurred',
        timestamp: new Date().toISOString()
      }, null, 2);
    }
  }

  /**
   * Fetch LinkedIn context with optional posts summary
   */
  private async fetchLinkedInContext(
    linkedinUrl?: string,
    includePostsSummary: boolean = true
  ): Promise<string> {
    if (!linkedinUrl) {
      return 'LinkedIn URL not provided. Context unavailable.';
    }

    let context = `# LinkedIn Context\n\nThis context is derived from LinkedIn. Use only facts present here; do not infer private data.\n\n`;

    context += `**Profile URL:** ${linkedinUrl}\n\n`;

    if (includePostsSummary) {
      try {
        // Use LinkedIn tools to get posts
        const postsResult = await this.linkedinTools.execute({
          profile_url: linkedinUrl,
          limit: 5
        });

        const bundle = JSON.parse(postsResult);
        if (bundle.posts && bundle.posts.length > 0) {
          const themeSummary = ThemeInferenceEngine.generateThemeSummary(bundle.posts);
          context += `**Recent Activity Summary:** ${themeSummary}\n\n`;

          // Add a few recent post excerpts
          context += `**Recent Posts (excerpts):**\n`;
          bundle.posts.slice(0, 3).forEach((post: any, index: number) => {
            const excerpt = post.text.substring(0, 100) + (post.text.length > 100 ? '...' : '');
            context += `${index + 1}. ${excerpt}\n`;
          });
        }
      } catch (error) {
        context += `**Recent Activity:** Unable to fetch recent posts - ${error}\n\n`;
      }
    }

    return context;
  }

  /**
   * Fetch Apollo context (placeholder implementation)
   */
  private async fetchApolloContext(
    firstName: string,
    lastName: string,
    organizationName?: string,
    domain?: string,
    limit: number = 1
  ): Promise<{ context: string; candidates: CandidateProfile[] }> {
    // Placeholder implementation - Apollo integration coming soon
    const context = `# Apollo Context\n\nThis context is derived from Apollo.io. Use only facts present here; do not infer private data.\n\n**Note:** Apollo integration is a placeholder in this implementation.\n\n**Name:** ${firstName} ${lastName}\n${organizationName ? `**Organization:** ${organizationName}\n` : ''}${domain ? `**Domain:** ${domain}\n` : ''}\n**Status:** Placeholder candidate profile`;

    const candidates: CandidateProfile[] = [
      {
        candidate_id: uuidv4(),
        full_name: `${firstName} ${lastName}`,
        organization_name: organizationName ?? undefined,
        domain: domain ?? undefined,
        confidence: 0.7,
        source: 'apollo'
      }
    ];

    return { context, candidates };
  }

  /**
   * Create combined context from LinkedIn and Apollo data
   */
  private createCombinedContext(
    linkedinContext: string,
    apolloContext: string,
    firstName: string,
    lastName: string
  ): string {
    return `# Combined Context for ${firstName} ${lastName}

## From LinkedIn
${linkedinContext}

## From Apollo
${apolloContext}

---
*This combined context provides grounding for conversation openers. Only use information explicitly stated above.*`;
  }

  /**
   * Generate conversation openers based on contexts
   */
  private async generateOpeners(
    linkedinContext: string,
    apolloContext: string,
    postsSummary?: string,
    toneOptions: string[] = ['casual', 'professional', 'playful']
  ): Promise<Array<{ tone: string; text: string; why: string }>> {
    // Simple opener generation based on available context
    const openers = [];

    for (const tone of toneOptions.slice(0, 3)) {
      let opener = '';
      let rationale = '';

      switch (tone) {
        case 'casual':
          opener = this.generateCasualOpener(linkedinContext, apolloContext, postsSummary);
          rationale = 'Casual tone to create approachable first impression';
          break;
        case 'professional':
          opener = this.generateProfessionalOpener(linkedinContext, apolloContext, postsSummary);
          rationale = 'Professional tone highlighting mutual business interests';
          break;
        case 'playful':
          opener = this.generatePlayfulOpener(linkedinContext, apolloContext, postsSummary);
          rationale = 'Light and engaging approach to spark curiosity';
          break;
        default:
          opener = 'Hi! I came across your profile and would love to connect.';
          rationale = 'Generic opener when context is insufficient';
      }

      openers.push({
        tone,
        text: opener,
        why: rationale
      });
    }

    return openers;
  }

  private generateCasualOpener(linkedinContext: string, apolloContext: string, postsSummary?: string): string {
    if (postsSummary && postsSummary.includes('technology')) {
      return "Hey! Noticed you're in tech - always interesting to connect with fellow technologists. How's your week going?";
    }
    return "Hi there! Came across your profile and thought it'd be great to connect. Hope you're having a good week!";
  }

  private generateProfessionalOpener(linkedinContext: string, apolloContext: string, postsSummary?: string): string {
    const hasOrg = apolloContext.includes('Organization:');
    if (hasOrg) {
      return "Hello! I noticed your work in the industry and would love to connect to discuss potential synergies between our organizations.";
    }
    return "Hello! I came across your professional profile and would welcome the opportunity to connect and learn more about your work.";
  }

  private generatePlayfulOpener(linkedinContext: string, apolloContext: string, postsSummary?: string): string {
    if (postsSummary && postsSummary.includes('entrepreneurship')) {
      return "Hi! Fellow entrepreneur here 🚀 Always love connecting with people building cool things. What's your latest project?";
    }
    return "Hi! Your profile caught my attention - looks like you're doing some interesting work! Would love to connect and chat sometime.";
  }

  /**
   * Get a stored resource by URI
   */
  getResource(uri: string): string | undefined {
    return this.resourceStorage.get(uri);
  }

  /**
   * List all available resource URIs
   */
  listResources(): string[] {
    return Array.from(this.resourceStorage.keys());
  }
}