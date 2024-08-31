await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT if upload_type == "document" else ChatAction.UPLOAD_PHOTO)
                if upload_type == "document":
                    await message.reply_to_message.reply_document(edit_img_loc, quote=True)
                else:
                    await message.reply_to_message.reply_photo(edit_img_loc, quote=True)

                await msg.delete()
            else:
                await message.reply_text("Why
