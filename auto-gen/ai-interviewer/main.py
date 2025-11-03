from ai_interviewer import team_Config, interview
import asyncio

async def main():
    job_position = "Software Engineer"
    team = await team_Config(job_position)

    async for returnedMsg in interview(team):
        print('-'*70)
        ##print(type(message))
        print(returnedMsg)

if __name__ == "__main__":
    asyncio.run(main())