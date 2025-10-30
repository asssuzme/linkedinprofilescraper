# Output Schema Documentation

This document describes the complete JSON output schema for scraped LinkedIn profiles.

## Top-Level Structure

```json
[
  {
    // Profile object
  }
]
```

The output is always an array of profile objects, even for a single profile.

## Profile Object Schema

### Basic Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `linkedinUrl` | string | Full LinkedIn profile URL | `"https://www.linkedin.com/in/johndoe"` |
| `firstName` | string | First name | `"John"` |
| `lastName` | string | Last name | `"Doe"` |
| `fullName` | string | Full name as displayed | `"John Doe"` |
| `headline` | string | Profile headline | `"Software Engineer at Tech Corp"` |
| `connections` | integer | Number of connections | `500` |
| `followers` | integer | Number of followers | `750` |
| `publicIdentifier` | string | LinkedIn public ID | `"johndoe"` |
| `urn` | string | LinkedIn URN identifier | `"ACoAAABCDEF..."` |
| `openConnection` | boolean | Whether profile accepts connection requests | `true` |

### Contact Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `email` | string\|null | Email address (if available) | `"john@example.com"` |
| `mobileNumber` | string\|null | Phone number (if available) | `"+1-234-567-8900"` |

### Location

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `addressWithCountry` | string | Full address with country | `"San Francisco, California, United States"` |
| `addressWithoutCountry` | string | Address without country | `"San Francisco, California"` |
| `addressCountryOnly` | string | Country only | `"United States"` |

### Profile Pictures

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `profilePic` | string | Standard resolution (200x200) | `"https://media.licdn.com/..."` |
| `profilePicHighQuality` | string | High resolution (800x800) | `"https://media.licdn.com/..."` |
| `profilePicAllDimensions` | array | All available dimensions | See structure below |

#### Profile Picture Dimensions Structure
```json
{
  "width": 200,
  "height": 200,
  "url": "https://media.licdn.com/..."
}
```

### Current Job Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `jobTitle` | string | Current job title | `"Senior Software Engineer"` |
| `companyName` | string | Current company name | `"Tech Corp"` |
| `companyIndustry` | string | Company industry | `"Information Technology"` |
| `companyWebsite` | string | Company website | `"techcorp.com"` |
| `companyLinkedin` | string | Company LinkedIn URL | `"linkedin.com/company/techcorp"` |
| `companyFoundedIn` | integer\|null | Year company was founded | `2010` |
| `companySize` | string | Company size range | `"201-500"` |
| `currentJobDuration` | string | Duration at current job | `"2 yrs 3 mos"` |
| `currentJobDurationInYrs` | float | Duration in years | `2.25` |

### About

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `about` | string | Profile about/summary section | `"Passionate software engineer with..."` |

### Skills

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `topSkillsByEndorsements` | string | Top 5 skills (comma-separated) | `"Python, JavaScript, React, AWS, Docker"` |
| `skills` | array | Detailed skills array | See structure below |

#### Skills Array Structure
```json
{
  "title": "Python",
  "subComponents": [
    {
      "description": [
        {
          "type": "insightComponent",
          "text": "Software Engineer at Tech Corp"
        },
        {
          "type": "insightComponent",
          "text": "15 endorsements"
        }
      ]
    }
  ]
}
```

### Experience

Array of work experience objects. Supports both single-role and multi-role (breakdown) formats.

#### Single Role Format
```json
{
  "companyId": "123456",
  "companyUrn": "urn:li:fsd_company:123456",
  "companyLink1": "https://www.linkedin.com/company/123456/",
  "logo": "https://media.licdn.com/...",
  "title": "Tech Corp",
  "subtitle": "Full-time · 2 yrs 3 mos",
  "caption": "San Francisco, California",
  "breakdown": false,
  "subComponents": [
    {
      "title": "Senior Software Engineer",
      "caption": "Jan 2023 - Present · 2 yrs",
      "metadata": "Full-time",
      "description": [
        {
          "type": "textComponent",
          "text": "Led team of 5 engineers..."
        }
      ]
    }
  ]
}
```

#### Multiple Roles Format (breakdown: true)
```json
{
  "companyId": "123456",
  "companyUrn": "urn:li:fsd_company:123456",
  "companyLink1": "https://www.linkedin.com/company/123456/",
  "logo": "https://media.licdn.com/...",
  "title": "Tech Corp",
  "subtitle": "Full-time · 4 yrs 6 mos",
  "caption": "San Francisco, California",
  "breakdown": true,
  "subComponents": [
    {
      "title": "Senior Software Engineer",
      "caption": "Jan 2023 - Present · 2 yrs",
      "metadata": "Full-time",
      "description": [...]
    },
    {
      "title": "Software Engineer",
      "caption": "Jul 2020 - Dec 2022 · 2 yrs 6 mos",
      "metadata": "Full-time",
      "description": [...]
    }
  ]
}
```

### Education

Array of education objects.

```json
{
  "companyId": "12345",
  "companyUrn": "urn:li:fsd_company:12345",
  "companyLink1": "https://www.linkedin.com/school/12345/",
  "logo": "https://media.licdn.com/...",
  "title": "Stanford University",
  "subtitle": "Bachelor of Science - BS, Computer Science",
  "caption": "2016 - 2020",
  "breakdown": false,
  "subComponents": [
    {
      "description": [
        {
          "type": "insightComponent",
          "text": "Grade: 3.8 GPA"
        }
      ]
    }
  ]
}
```

### Licenses and Certificates

Array of certification objects.

```json
{
  "companyId": "1337",
  "companyUrn": "urn:li:fsd_company:1337",
  "companyLink1": "https://www.linkedin.com/company/1337/",
  "logo": "https://media.licdn.com/...",
  "title": "AWS Certified Solutions Architect",
  "subtitle": "Amazon Web Services (AWS)",
  "caption": "Issued Jan 2024 · Expires Jan 2027",
  "breakdown": false,
  "subComponents": [
    {
      "description": []
    }
  ]
}
```

### Languages

Array of language objects.

```json
{
  "title": "English",
  "caption": "Native or bilingual proficiency",
  "breakdown": false,
  "subComponents": [
    {
      "description": []
    }
  ]
}
```

### Recommendations

Array with two sections: Received and Given.

```json
{
  "section_name": "Received",
  "section_components": [
    {
      "titleV2": "Jane Smith",
      "caption": "March 15, 2024, Jane was John's client",
      "subtitle": "Product Manager at Example Corp",
      "size": "LARGE",
      "textActionTarget": "https://www.linkedin.com/in/janesmith",
      "image": "https://media.licdn.com/...",
      "subComponents": [
        {
          "fixedListComponent": [
            {
              "type": "textComponent",
              "text": "John was an excellent engineer..."
            }
          ]
        }
      ]
    }
  ]
}
```

### Interests

Array of interest sections (Companies, Groups, Schools, Newsletters, Top Voices).

```json
{
  "section_name": "Companies",
  "section_components": [
    {
      "titleV2": "Google",
      "caption": "1,234,567 followers",
      "subtitle": "",
      "size": "LARGE",
      "textActionTarget": "https://www.linkedin.com/company/1234/",
      "subComponents": []
    }
  ]
}
```

### Other Fields

The following fields are included but may be empty arrays:

- `honorsAndAwards` - Array of honors and awards
- `volunteerAndAwards` - Array of volunteer experience
- `verifications` - Array of profile verifications
- `promos` - Array of promotional content
- `highlights` - Array of profile highlights
- `projects` - Array of projects
- `publications` - Array of publications
- `patents` - Array of patents
- `courses` - Array of courses
- `testScores` - Array of test scores
- `organizations` - Array of organizations
- `volunteerCauses` - Array of volunteer causes
- `updates` - Array of recent activity updates

## Example Complete Profile

See the example output in the repository for a complete profile object with all fields populated.

## Notes

- All arrays can be empty `[]` if the data is not available
- String fields use `""` (empty string) as default
- Nullable fields use `null` when not available
- Integer fields use `0` as default
- Boolean fields default to `false`
- URLs are cleaned (tracking parameters removed)
- Profile pictures are available in multiple resolutions

## Data Availability

Not all profiles will have all data available due to:
- Privacy settings
- Incomplete profiles
- LinkedIn's visibility rules
- Connection status with the scraper account

The scraper handles missing data gracefully and provides defaults for all fields.
