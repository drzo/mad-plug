import { joinSession } from "@github/copilot-sdk/extension";

// time-crystal-daemon — Knowledge-based skill plugin
// This plugin exposes the skill as a guidance tool

await joinSession({
    tools: [
        {
            name: "time_crystal_daemon_guide",
            description: "Provide guidance using the time-crystal-daemon skill knowledge base. Returns structured knowledge for the given topic.",
            parameters: {
                type: "object",
                properties: {
                    topic: {
                        type: "string",
                        description: "The topic or concept to get guidance about"
                    },
                    context: {
                        type: "string",
                        description: "Optional context to narrow down the guidance"
                    }
                },
                required: ["topic"]
            },
            handler: async (args) => {
                // Knowledge-based plugins return skill documentation
                // The skill content serves as the knowledge base
                return `# time-crystal-daemon Guidance

## Topic: ${args.topic}
${args.context ? `Context: ${args.context}` : ""}

Refer to the skill documentation in skills/time-crystal-daemon/SKILL.md for detailed guidance on this topic.

This is a knowledge-based plugin. Use the skill documentation as your primary reference.`;
            }
        }
    ]
});
