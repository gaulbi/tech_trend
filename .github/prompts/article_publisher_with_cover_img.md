

## Modification Instruction
1. Modify hashnode.py 

## Upload Article to Hashnode

### Hashnode Publishing (GraphQL v2)
**`PublishPost` mutation**:  
```graphql
  mutation PublishPost($input: PublishPostInput!) {
    publishPost(input: $input) {
      post { 
        id 
        slug 
        title
        coverImage {
            ...PostCoverImageFragment
        }
      }
    }
  }
```

**`CoverImageOptionsInput`**  
```json
{
  "coverImageURL": "xyz789",
  "isCoverAttributionHidden": true,
  "stickCoverToBottom": false
}
```

---