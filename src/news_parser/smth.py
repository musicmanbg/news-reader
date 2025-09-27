if __name__ == "__main__":
    
    print ("hi there!")

#     print ("hi there!")
#     from kokoro import KPipeline
#     import soundfile as sf
#     import torch
#     pipeline = KPipeline(lang_code='a')
#     text = '''
#     With Bulgaria preparing to adopt the euro, merchants and consumers will benefit from a smoother, more efficient payment system. The elimination of currency conversion costs between the lev and the euro, along with simplified reporting and easier service for foreign clients, is expected to make business operations more transparent and manageable. Companies such as myPOS emphasize that careful preparation, clear communication, and automated tools are key to a seamless transition.Card payments and POS terminals are particularly valuable during this process. These systems automate conversions, reduce human error, and build customer trust. myPOS reports that upgrades to POS terminals, account conversions, and card reissuance will all occur remotely at the official fixed exchange rate of 1.95583, with no disruption to services. Merchants will only need to follow a few simple steps on the terminals themselves to complete updates.
# Experience from Croatia’s euro adoption in 2023, coupled with myPOS’s work with over 300,000 businesses across 35 European markets, demonstrates that with good preparation and institutional support, merchants can adapt efficiently. POS terminals display amounts in both currencies during the transitional phase, ensuring clarity and transparency at checkout. Card payments eliminate errors associated with cash, speed up transactions, and enhance security, which is particularly valuable for foreign customers. The switch to the euro also provides operational advantages. Merchants no longer need to handle cash in euro cents, easing daily routines. Business accounts will automatically convert to euro IBANs, daily statements and invoices will be issued in euros, and business cards will be reissued with euro data. Both old and new cards will function for a short overlap period, with an option for early adoption, but full migration is required by December 31, 2025.
# Additional benefits include convenience for tourists, who can pay in a familiar currency, and the encouragement of modern, cashless payment habits among Bulgarian consumers. Meanwhile, automated solutions from providers like myPOS allow merchants to focus on business growth while technical transitions are managed professionally. The deadline for updating all POS and fiscal devices is October 8, 2025. Remote updates for myPOS devices will ensure full functionality in euros without merchant intervention. Failure to comply after this date may result in legal sanctions, as outlined in official regulations. Polina Toskova, myPOS Country Manager for Bulgaria, stresses that the transition should be viewed as an opportunity rather than a challenge. The automated migration of accounts, terminals, and cards ensures smooth daily operations, reduces errors, and supports business organization. Integration with European markets, combined with transparency and security in payments, positions Bulgarian merchants to benefit from faster, safer, and more efficient financial operations.
# This transition represents the largest financial change Bulgaria has seen in decades, offering tangible advantages for merchants and consumers alike, from simpler reporting and reduced costs to increased trust and smoother service for international clients.
#     '''
    
#     # print(torch.cuda.is_available())
#     generator = pipeline(text, voice='af_heart')
#     for i, (gs, ps, audio) in enumerate(generator):
#         print(f"Generated audio chunk {i}: graphemes='{gs}', phonemes='{ps}'")
#         sf.write(f'{i}.wav', audio, 24000)